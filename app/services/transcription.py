import io
import openai
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI()

def transcribe_audio(audio_bytes):
    """
    Handles incoming audio. 
    Now expects a valid WAV file (starting with b'RIFF') from the client.
    """
    try:
        # 1. Validation: Check if it's actually a WAV file
        # A valid WAV file always starts with the bytes "RIFF"
        if not audio_bytes.startswith(b'RIFF'):
            print(f"⚠️ Error: Received {len(audio_bytes)} bytes, but missing WAV header (RIFF).")
            print("   Make sure Unity is encoding to WAV, not just sending raw samples.")
            return ""

        # 2. Prepare for OpenAI
        # We wrap the bytes in a BytesIO object so it looks like a file
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav"  # Important: OpenAI needs a filename extension

        # 3. Transcribe
        print(f"👂 Transcribing {len(audio_bytes)} bytes...")
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