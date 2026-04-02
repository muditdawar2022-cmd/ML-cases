#!/usr/bin/env python3
"""Interview Story Coach - Complete Version with PyAudio"""

import os
import sys
from pathlib import Path

# Fix Windows encoding for arrow characters
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
from typing import Optional, Dict, Tuple

import pyaudio
import wave
from google.cloud import speech_v1
from anthropic import Anthropic
from notion_client import Client

# RAG imports
import numpy as np
from sentence_transformers import SentenceTransformer

load_dotenv()

SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 1024
AUDIO_DIR = Path("C:/Users/Mudit Dawar/capstone/interview coach/Recording")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_FILE = AUDIO_DIR / "interview_question.wav"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_PAGE_ID = os.getenv("NOTION_FIT_STORIES_PAGE_ID")

def validate_setup():
    """Validate credentials."""
    errors = []
    if not ANTHROPIC_API_KEY:
        errors.append("ANTHROPIC_API_KEY")
    if not NOTION_API_KEY:
        errors.append("NOTION_API_KEY")
    if not NOTION_PAGE_ID:
        errors.append("NOTION_FIT_STORIES_PAGE_ID")
    
    if errors:
        print(f"Missing in .env: {', '.join(errors)}")
        sys.exit(1)

def record_audio_pyaudio(device_index: int = None) -> Optional[bytes]:
    """Record audio using PyAudio - ENTER to stop."""
    import threading
    
    p = pyaudio.PyAudio()
    
    try:
        if device_index is None:
            device_info = p.get_default_input_device_info()
            device_index = int(device_info['index'])
        else:
            device_info = p.get_device_info_by_index(device_index)
        
        print(f"Recording from: {device_info['name']}")
        
        stream = p.open(
            format=pyaudio.paInt16,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=CHUNK_SIZE
        )
        
        print("Recording... (press ENTER to stop)")
        frames = []
        stop_recording = threading.Event()
        
        def record_thread():
            while not stop_recording.is_set():
                data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                frames.append(data)
        
        # Start recording in background thread
        thread = threading.Thread(target=record_thread, daemon=True)
        thread.start()
        
        # Wait for user to press ENTER
        input()
        stop_recording.set()
        thread.join(timeout=1)
        
        print("Stopped recording")
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        return b''.join(frames)
        
    except Exception as e:
        print(f"Recording error: {e}")
        p.terminate()
        return None

def save_wav(audio_data: bytes, filepath: Path):
    """Save audio to WAV file."""
    try:
        with wave.open(str(filepath), 'wb') as wav_file:
            wav_file.setnchannels(CHANNELS)
            wav_file.setsampwidth(2)
            wav_file.setframerate(SAMPLE_RATE)
            wav_file.writeframes(audio_data)
        print(f"Saved to {filepath}")
    except Exception as e:
        print(f"Error saving: {e}")

def transcribe_with_google(audio_file: Path) -> Optional[str]:
    """Transcribe using Google Cloud."""
    print("Transcribing...")
    
    try:
        client = speech_v1.SpeechClient()
        
        with open(audio_file, "rb") as f:
            content = f.read()
        
        audio = speech_v1.RecognitionAudio(content=content)
        config = speech_v1.RecognitionConfig(
            encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=SAMPLE_RATE,
            language_code="en-US",
        )
        
        response = client.recognize(config=config, audio=audio)
        
        transcript = ""
        for result in response.results:
            for alternative in result.alternatives:
                transcript += alternative.transcript
        
        if not transcript:
            print("No speech detected")
            return None
        
        print(f"Transcribed: {transcript}\n")
        return transcript.strip()
        
    except Exception as e:
        print(f"Transcription error: {e}")
        return None

class NotionStoriesFetcher:
    """Fetch stories from Notion."""
    
    def __init__(self, api_key: str, page_id: str):
        self.client = Client(auth=api_key)
        self.page_id = page_id.replace("-", "")
    
    def fetch_page_blocks(self) -> list:
        """Fetch blocks from page."""
        try:
            blocks = []
            cursor = None
            
            while True:
                response = self.client.blocks.children.list(
                    self.page_id,
                    start_cursor=cursor,
                    page_size=100
                )
                blocks.extend(response.get("results", []))
                
                if not response.get("has_more"):
                    break
                cursor = response.get("next_cursor")
            
            return blocks
        except Exception as e:
            print(f"Error fetching blocks: {e}")
            return []
    
    def parse_stories_from_blocks(self, blocks: list) -> Dict[str, str]:
        """Parse blocks into stories."""
        if not blocks:
            return {}
        
        stories = {}
        current_story = None
        current_content = []
        
        for block in blocks:
            block_type = block.get("type")
            block_text = None
            
            if block_type in ["heading_1", "heading_2", "heading_3"]:
                heading_data = block.get(block_type, {})
                text_parts = heading_data.get("rich_text", [])
                if text_parts:
                    block_text = "".join([t.get("text", {}).get("content", "") for t in text_parts])
            
            elif block_type == "paragraph":
                paragraph = block.get("paragraph", {})
                text_parts = paragraph.get("rich_text", [])
                if text_parts:
                    block_text = "".join([t.get("text", {}).get("content", "") for t in text_parts])
            
            elif block_type == "bulleted_list_item":
                item = block.get("bulleted_list_item", {})
                text_parts = item.get("rich_text", [])
                if text_parts:
                    block_text = "".join([t.get("text", {}).get("content", "") for t in text_parts])
                    if block_text:
                        block_text = f"• {block_text}"
            
            is_story_title = (
                block_type in ["heading_1", "heading_2", "heading_3"] or
                (block_text and (block_text.startswith("##") or block_text.startswith("#")))
            )
            
            if is_story_title and block_text:
                if current_story and current_content:
                    stories[current_story] = "\n".join(current_content)
                    current_content = []
                
                current_story = block_text.lstrip("#").strip()
                print(f"   Found story: {current_story}")
            
            elif block_text and block_text.strip() and current_story:
                current_content.append(block_text)
        
        if current_story and current_content:
            stories[current_story] = "\n".join(current_content)
        
        return stories
    
    def fetch_all_stories(self) -> Dict[str, str]:
        """Fetch all stories."""
        print("Fetching stories from Notion...")
        blocks = self.fetch_page_blocks()
        stories = self.parse_stories_from_blocks(blocks)
        print(f"Loaded {len(stories)} stories\n")
        return stories

def load_transcript_history() -> str:
    """Load previous transcript history."""
    transcript_file = Path("interview_transcript.txt")
    if transcript_file.exists():
        with open(transcript_file, "r") as f:
            return f.read()
    return ""

def save_to_transcript(question: str, answer: str):
    """Append Q&A to transcript file."""
    transcript_file = Path("interview_transcript.txt")
    with open(transcript_file, "a") as f:
        f.write(f"\nQ: {question}\n\nA: {answer}\n\n" + "─" * 60 + "\n")

def is_generic(question: str) -> bool:
    """Check if question is generic (not story-based)."""
    generic_keywords = [
        "how would you", "how will you", "what would you",
        "walk me through", "explain", "design",
        "improve", "build", "strategy", "product"
    ]
    q = question.lower()
    
    if "tell me about a time" in q or "example" in q:
        return False
    
    return any(kw in q for kw in generic_keywords)

def find_best_story_rag(question: str, stories: Dict[str, str]) -> Tuple[Optional[str], float]:
    """Find best matching story using semantic search (RAG)."""
    if not stories:
        return None, 0.0
    
    print("Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Encode question
    question_embedding = model.encode(question)
    
    # Encode all stories (concatenate title + content for better matching)
    best_story = None
    best_score = -1
    
    for story_name, story_content in stories.items():
        # Combine title and content for richer context
        full_text = f"{story_name}. {story_content[:500]}"
        story_embedding = model.encode(full_text)
        
        # Calculate cosine similarity
        similarity = np.dot(question_embedding, story_embedding) / (
            np.linalg.norm(question_embedding) * np.linalg.norm(story_embedding)
        )
        
        if similarity > best_score:
            best_score = similarity
            best_story = story_name
    
    return best_story, best_score

def find_best_story(question: str, stories: Dict[str, str], client: Anthropic) -> Tuple[Optional[str], str]:
    """Find best matching story - uses RAG or generic detection."""
    if is_generic(question):
        return None, "generic"
    
    if not stories:
        return None, "generic"
    
    # Use semantic search (RAG)
    best_story, similarity_score = find_best_story_rag(question, stories)
    
    print(f"Matched: {best_story} (confidence: {similarity_score:.2f})")
    
    # If similarity is too low, treat as generic
    if similarity_score < 0.3:
        print("Confidence too low, using generic answer")
        return None, "generic"
    
    if best_story:
        return best_story, "story"
    return None, "generic"

def generate_nuggets(story_name: str, story_content: str, question: str, client: Anthropic) -> str:
    """Generate STAR format nuggets from story - small, scannable bullets."""
    prompt = f"""Question: "{question}"

Story: {story_name}

Content:
{story_content}

Generate a STAR format summary with small, scannable nuggets (talking points, not a script):

Format:
📌 Story: {story_name}

Situation: [Brief 1-line context]
Task: [What you had to do]
Action: [Key actions taken - use bullets with →]
→ [Action 1]
→ [Action 2]
→ [Action 3]
Result: [Impact/outcome with numbers if available]

Keep EACH line SHORT (under 100 chars). Make it scannable talking points."""

    response = client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text

def generate_answer(question: str, stories: Dict[str, str], history: str, client: Anthropic) -> str:
    """Generate answer for generic question - structured reference bullets."""
    context = "\n\n".join([
        f"Story: {t}\n{c}"
        for t, c in list(stories.items())[:3]
    ])
    
    history_context = f"\nPrevious conversation:\n{history}" if history else ""
    
    prompt = f"""Background:
{context}{history_context}

Question: "{question}"

Provide a STRUCTURED ANSWER with reference bullets (NOT a script - just anchors).

Format like this:
Goal/Problem: [What you're solving]
[Key insight/approach]
[Diagnosis/Why]
[Opportunities/Levers:]
→ [Option 1]
→ [Option 2]
→ [Option 3]
Solutions:
[Solution approach]
Metrics:
↑ [Success metric 1]
↓ [Success metric 2]
Risks / tradeoffs:
[Key risk 1]
[Key risk 2]

Use bullets as TALKING POINTS, not a memorized script."""

    response = client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text

def main():
    """Main loop."""
    validate_setup()
    
    print("\nInitializing...\n")
    
    fetcher = NotionStoriesFetcher(NOTION_API_KEY, NOTION_PAGE_ID)
    stories = fetcher.fetch_all_stories()
    
    if not stories:
        print("No stories found")
        sys.exit(1)
    
    history = load_transcript_history()
    if history:
        print("Loaded previous conversation\n")
    
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    
    print("""
╔════════════════════════════════════════════════════════════╗
║              Interview Story Coach                         ║
║              Press ENTER to record question               ║
╚════════════════════════════════════════════════════════════╝

Commands: 'text' (type), 'clear' (clear history), 'quit'
""")
    
    text_mode = False
    
    while True:
        try:
            if text_mode:
                print("\nQuestion (or 'voice'/'clear'/'quit'):")
                question = input("> ").strip()
                
                if question.lower() == 'quit':
                    print("Bye!")
                    break
                elif question.lower() == 'voice':
                    text_mode = False
                    continue
                elif question.lower() == 'clear':
                    Path("interview_transcript.txt").unlink(missing_ok=True)
                    history = ""
                    print("Transcript cleared")
                    continue
                elif not question:
                    continue
            else:
                print("\nPress ENTER to record (or type 'text'/'quit'):")
                cmd = input()
                
                if cmd.lower() == 'quit':
                    print("Bye!")
                    break
                elif cmd.lower() == 'text':
                    text_mode = True
                    continue
                
                audio_data = record_audio_pyaudio()
                if not audio_data:
                    continue
                
                save_wav(audio_data, AUDIO_FILE)
                question = transcribe_with_google(AUDIO_FILE)
                
                if not question:
                    continue
            
            print("Analyzing...")
            story_name, qtype = find_best_story(question, stories, client)
            
            print("\nAnswer:")
            print("─" * 60)
            
            if qtype == "story" and story_name:
                answer = generate_nuggets(story_name, stories[story_name], question, client)
            else:
                answer = generate_answer(question, stories, history, client)
            
            print(answer)
            print("─" * 60)
            
            save_to_transcript(question, answer)
            history = load_transcript_history()
            
        except KeyboardInterrupt:
            print("\nBye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
