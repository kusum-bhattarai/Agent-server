import os
import io
import openai
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI Client
client = openai.OpenAI()

def transcribe_audio(audio_bytes):
    """
    Takes raw audio bytes (WAV/WEBM) and sends them to OpenAI Whisper.
    Returns: The transcribed text string.
    """
    try:
        # 1. Create a "virtual file" in memory
        # OpenAI needs a 'file-like' object with a name.
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav" 

        # 2. Call Whisper API
        print("👂 Transcribing audio...")
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="en"
        )
        
        text = transcript.text
        print(f"📝 Heard: '{text}'")
        return text

    except Exception as e:
        print(f"❌ Transcription Error: {e}")
        return ""