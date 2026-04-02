# Interview Story Coach - Complete Setup Guide

## What You Need

1. **Python 3.8+** installed on your computer
2. **API Keys:**
   - Anthropic API key (for Claude)
   - Google Cloud Speech-to-Text API key
   - Notion API key
3. **Notion page ID** for your FIT STORIES

---

## Step 1: Get API Keys

### A) Anthropic API Key
1. Go to: https://console.anthropic.com/
2. Sign up or login
3. Go to **API Keys** section
4. Click **Create Key**
5. Copy the key (looks like: `sk-ant-...`)

### B) Google Cloud Speech-to-Text
1. Go to: https://console.cloud.google.com/
2. Create a new project called "Interview Coach"
3. Enable **Speech-to-Text API**
4. Go to **Service Accounts** → Create service account
5. Download JSON key file
6. Save it somewhere safe (we'll reference it later)

### C) Notion API Key
1. Go to: https://www.notion.so/my-integrations
2. Click **New integration**
3. Name it "Interview Coach"
4. Copy the **Internal Integration Token**

### D) Notion Page ID
1. Open your **FIT STORIES** page in Notion
2. Copy the URL (looks like):
   ```
   https://www.notion.so/workspace/FIT-STORIES-1a2b3c4d5e6f7g8h
   ```
3. The page ID is the last 32 characters: `1a2b3c4d5e6f7g8h...`

---

## Step 2: Setup Files

Create a folder for Interview Coach:
```
C:\Users\YourName\interview_coach\
├── interview_coach_pyaudio.py      (main script)
├── requirements.txt                 (dependencies)
├── .env                             (your credentials - KEEP SECRET!)
├── .env.example                     (template)
├── google-key.json                  (Google Cloud service account key)
├── interview_transcript.txt         (auto-generated transcript)
└── Recording/                       (folder for audio files)
```

---

## Step 3: Create .env File

Create a file called `.env` in your interview_coach folder:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
NOTION_API_KEY=noti_your-key-here
NOTION_FIT_STORIES_PAGE_ID=1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p
GOOGLE_APPLICATION_CREDENTIALS=C:\Users\YourName\interview_coach\google-key.json
```

Replace values with your actual keys.

---

## Step 4: Save Google Cloud Key

1. Download the JSON file from Google Cloud
2. Save it in your interview_coach folder as `google-key.json`
3. Update the `GOOGLE_APPLICATION_CREDENTIALS` path in `.env` to point to it

---

## Step 5: Install Dependencies

Open terminal/command prompt in your interview_coach folder:

```bash
pip install -r requirements.txt
```

This installs all required packages.

---

## Step 6: Test It

```bash
python interview_coach_pyaudio.py
```

You should see:
```
Initializing...

Fetching stories from Notion...
   Found story: [Your Story 1]
   Found story: [Your Story 2]
Loaded X stories

Ready!

Press ENTER to record (or type 'text'/'quit'):
```

---

## How to Use

### Recording a Question
```
Press ENTER to record (or type 'text'/'quit'):
[Press ENTER]
Recording from: Microphone Array...
Recording... (press ENTER to stop)
[Speak your question]
[Press ENTER]
```

### Using Text Mode
```
Press ENTER to record (or type 'text'/'quit'):
text
Question (or 'voice'/'clear'/'quit'):
> Tell me about a time you led a team
```

### Commands
- **ENTER** → Record voice question
- **text** → Switch to typing questions
- **voice** → Switch back to voice mode
- **clear** → Clear transcript history
- **quit** → Exit

---

## Troubleshooting

### "No speech detected"
- Make sure your microphone is working
- Speak louder and clearer
- Check microphone isn't muted

### "GOOGLE_APPLICATION_CREDENTIALS not set"
- Make sure the path in `.env` is correct
- Use full absolute path, not relative

### "Your credit balance is too low"
- Go to https://console.anthropic.com/
- Add credits ($5-10 is plenty)

### "Notion API error"
- Check your `NOTION_API_KEY` is correct
- Make sure you shared your FIT STORIES page with the integration

---

## Security Notes

⚠️ **IMPORTANT:**
- Never share your `.env` file (it has your API keys!)
- Add `.env` to `.gitignore` if uploading to GitHub
- Keep your Google Cloud JSON key safe
- Rotate API keys regularly

---

## Files to Share

To share with someone else, provide:
1. `interview_coach_pyaudio.py`
2. `requirements.txt`
3. `.env.example` (without actual keys)
4. `SETUP_GUIDE.md` (this file)

They need to:
1. Get their own API keys
2. Create their own `.env` file
3. Run `pip install -r requirements.txt`
4. Run the script

---

## Next Steps

1. ✅ Get all API keys
2. ✅ Create `.env` file
3. ✅ Install dependencies
4. ✅ Test with a question
5. ✅ Share with team/friends

Good luck! 🎤
