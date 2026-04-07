const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');

const API_KEY = 'YOUR_API_KEY_HERE'; // ← paste your Anthropic API key here
const PORT = 3000;

const MIME_TYPES = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'application/javascript',
};

const server = http.createServer((req, res) => {
  // CORS headers for all responses
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    return res.end();
  }

  // URL fetcher route — follows redirects up to 5 hops
  if (req.method === 'POST' && req.url === '/api/fetch-url') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      let url;
      try { url = JSON.parse(body).url; } catch(e) { res.writeHead(400); return res.end(JSON.stringify({ error: 'Invalid JSON' })); }
      if (!url) { res.writeHead(400); return res.end(JSON.stringify({ error: 'No URL provided' })); }

      function doFetch(currentUrl, hopsLeft) {
        if (hopsLeft === 0) {
          res.writeHead(200, { 'Content-Type': 'application/json' });
          return res.end(JSON.stringify({ error: 'Too many redirects' }));
        }
        let parsed;
        try { parsed = new URL(currentUrl); } catch(e) {
          res.writeHead(200, { 'Content-Type': 'application/json' });
          return res.end(JSON.stringify({ error: 'Invalid URL: ' + currentUrl }));
        }
        const lib = parsed.protocol === 'https:' ? https : http;
        const options = {
          hostname: parsed.hostname,
          path: parsed.pathname + parsed.search,
          method: 'GET',
          headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,text/plain,application/json,*/*',
            'Accept-Language': 'en-US,en;q=0.9'
          }
        };
        const fetchReq = lib.request(options, fetchRes => {
          if ([301,302,303,307,308].includes(fetchRes.statusCode) && fetchRes.headers.location) {
            const location = fetchRes.headers.location;
            const nextUrl = location.startsWith('http') ? location : `${parsed.protocol}//${parsed.hostname}${location}`;
            fetchRes.resume(); // drain response
            return doFetch(nextUrl, hopsLeft - 1);
          }
          let data = '';
          fetchRes.on('data', chunk => data += chunk);
          fetchRes.on('end', () => {
            const contentType = fetchRes.headers['content-type'] || '';
            let text;
            if (contentType.includes('text/plain') || !contentType.includes('html')) {
              // Plain text — use directly (Google Docs export format=txt)
              text = data.trim();
            } else {
              // HTML — strip tags
              text = data
                .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
                .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
                .replace(/<[^>]+>/g, ' ')
                .replace(/\s{2,}/g, ' ')
                .trim();
            }
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ content: text.substring(0, 20000) }));
          });
        });
        fetchReq.on('error', err => {
          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: err.message }));
        });
        fetchReq.end();
      }

      doFetch(url, 5);
    });
    return;
  }

  // API proxy route
  if (req.method === 'POST' && req.url === '/api/chat') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      const options = {
        hostname: 'api.anthropic.com',
        path: '/v1/messages',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': API_KEY,
          'anthropic-version': '2023-06-01',
          'Content-Length': Buffer.byteLength(body)
        }
      };

      const apiReq = https.request(options, apiRes => {
        let data = '';
        apiRes.on('data', chunk => data += chunk);
        apiRes.on('end', () => {
          res.writeHead(apiRes.statusCode, { 'Content-Type': 'application/json' });
          res.end(data);
        });
      });

      apiReq.on('error', err => {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: { message: err.message } }));
      });

      apiReq.write(body);
      apiReq.end();
    });
    return;
  }

  // Serve static files from public/
  let filePath = req.url === '/' ? '/public/index.html' : '/public' + req.url;
  filePath = path.join(__dirname, filePath);

  fs.readFile(filePath, (err, content) => {
    if (err) {
      res.writeHead(404);
      return res.end('Not found');
    }
    const ext = path.extname(filePath);
    res.writeHead(200, { 'Content-Type': MIME_TYPES[ext] || 'text/plain' });
    res.end(content);
  });
});

server.listen(PORT, () => {
  console.log('');
  console.log('  ✓ Voice Assistant running!');
  console.log(`  ✓ Open this in Chrome: http://localhost:${PORT}`);
  console.log('');
  console.log('  Press Ctrl+C to stop');
  console.log('');
});
