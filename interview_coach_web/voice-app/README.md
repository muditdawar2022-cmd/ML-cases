# Voice Assistant — Deploy to Vercel

## Files
- `public/index.html` — the web app
- `api/chat.js` — serverless proxy to Anthropic API
- `vercel.json` — routing config

## Deploy in 5 steps

### 1. Push to GitHub
Create a new repo on github.com, then:
```
git init
git add .
git commit -m "voice assistant"
git remote add origin https://github.com/YOUR_USERNAME/voice-assistant.git
git push -u origin main
```

### 2. Go to vercel.com
- Sign up / log in (free)
- Click "Add New Project"
- Import your GitHub repo

### 3. Add your API key
In Vercel project settings → Environment Variables:
- Name: `ANTHROPIC_API_KEY`
- Value: `sk-ant-...your key...`

### 4. Deploy
Click Deploy — takes about 30 seconds.

### 5. Share the URL
Vercel gives you a URL like `https://voice-assistant-abc123.vercel.app`
Send that to anyone — works on phone and desktop.

## Notes
- Free Vercel plan is plenty for personal use
- API costs are on your Anthropic account (~$0.01 per conversation)
- Works on Chrome (desktop) and Safari (iPhone)
