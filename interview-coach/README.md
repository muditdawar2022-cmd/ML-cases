# Interview Story Coach 🎤

Real-time interview support powered by your Notion stories and Claude AI.

## What It Does

1. **Press ENTER** to record your interview question
2. **Speak** your question naturally
3. **Press ENTER** to stop recording
4. Claude **finds your best matching story** from Notion using RAG (semantic search)
5. Get **STAR format nuggets** or **structured answers** instantly
6. **Builds on previous context** - learns from your conversation history

## Quick Start (5 minutes)

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Setup Credentials
- Copy `.env.example` to `.env`
- Add your API keys (see SETUP_GUIDE.md)

### 3. Run
```bash
python interview_coach_pyaudio.py
```

### 4. Use It
```
Press ENTER to record (or type 'text'/'quit'):
[Press ENTER]
Recording from: Microphone Array...
[Speak your question]
[Press ENTER to stop]
Transcribing...
Analyzing...
Answer: [Story nuggets or direct answer]
```

## Requirements

- Python 3.8+
- Anthropic API key ($5+ credits)
- Google Cloud Speech-to-Text API key
- Notion API key + FIT STORIES page
- Microphone

## How It Works

### Voice Recording
Records continuously until you press ENTER. Uses PyAudio for Windows compatibility.

### Transcription
Converts speech to text using Google Cloud Speech-to-Text (very accurate).

### Story Matching (RAG)
- Fetches ALL stories from your Notion FIT STORIES page
- Uses `sentence-transformers` to embed your question
- Compares embeddings with story embeddings using cosine similarity
- Returns best matching story with confidence score

### Answer Generation
- **Story-based questions** ("Tell me about...") → STAR format nuggets
- **Generic questions** ("How would you...") → Structured answer with approach/diagnosis/solutions/metrics/risks

### Transcript History
Saves all Q&A to `interview_transcript.txt` and uses previous context for better answers.

## Commands

| Command | What It Does |
|---------|-------------|
| ENTER | Record a question (voice mode) |
| text | Switch to typing mode |
| voice | Switch back to recording mode |
| clear | Delete transcript history |
| quit | Exit the program |

## Files

- `interview_coach_pyaudio.py` - Main application
- `requirements.txt` - Python dependencies
- `.env` - Your API credentials (keep secret!)
- `.env.example` - Template for .env
- `interview_transcript.txt` - Saved Q&A history (auto-generated)
- `Recording/` - Folder for audio files

## Sharing With Others

To share this with someone:

1. **Upload to GitHub** (recommended):
   ```bash
   git init
   git add .
   git commit -m "Interview Story Coach"
   git push origin main
   ```

2. **Create .gitignore** to keep secrets safe:
   ```
   .env
   google-key.json
   interview_transcript.txt
   Recording/
   *.wav
   __pycache__/
   ```

3. **They need to**:
   - Clone the repo
   - Get their own API keys
   - Create their own `.env` file
   - Run `pip install -r requirements.txt`
   - Run the script

## Cloud Deployment

This runs **locally on your computer** with cloud APIs:
- ✅ Your audio records locally
- ✅ Transcription happens in Google Cloud
- ✅ AI analysis happens in Anthropic Cloud
- ✅ Stories fetched from Notion Cloud

**To run in the cloud** (Advanced):
- Deploy to AWS Lambda, Google Cloud Functions, or Heroku
- Would need to adapt recording for web/cloud environment
- Costs would be higher for cloud resources

For now, **running locally is simplest and cheapest**.

## Troubleshooting

**"No speech detected"** → Speak louder, closer to mic
**"API key error"** → Check .env file has correct keys
**"Notion error"** → Share your FIT STORIES page with the integration
**"Credit balance too low"** → Add credits at console.anthropic.com

## Cost Estimate

- Google Cloud Speech-to-Text: ~$0.024 per 15 seconds ($1.60/hour)
- Anthropic Claude: ~$0.003 per 1K tokens ($0.05-0.10 per question)
- **Total per interview**: ~$0.10-0.25

Very affordable! 💰

## Next Steps

1. Follow SETUP_GUIDE.md to setup
2. Test with a practice question
3. Use before your interviews
4. Share with friends/colleagues
5. Improve your interview game! 🚀

---

Built with ❤️ for better interviews.
