import io
import os
import torch
import whisper # This is the local library, not the API
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
# "base" is a good balance of speed and accuracy. 
# Options: "tiny", "base", "small", "medium", "large"
# If you have a dedicated NVIDIA GPU, this will run very fast.
MODEL_SIZE = "base"

print(f"⏳ Loading local Whisper model ({MODEL_SIZE})...")
try:
    # Check if CUDA (NVIDIA GPU) is available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"   - Running on: {device.upper()}")
    
    # Load the model into memory ONCE (don't load it inside the function!)
    model = whisper.load_model(MODEL_SIZE, device=device)
    print("✅ Whisper model loaded.")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None

def transcribe_audio(audio_bytes):
    """
    Handles incoming audio locally using the loaded Whisper model.
    """
    if model is None:
        return "Error: Whisper model not loaded."

    try:
        # 1. Validation: Check if it's actually a WAV file
        if not audio_bytes.startswith(b'RIFF'):
            print(f"⚠️ Error: Received {len(audio_bytes)} bytes, but missing WAV header.")
            return ""

        # 2. Save to a temporary file
        # Local Whisper needs a file path or a specialized numpy array. 
        # Saving to temp file is the safest, easiest method.
        temp_filename = "temp_audio.wav"
        with open(temp_filename, "wb") as f:
            f.write(audio_bytes)

        # 3. Transcribe
        print(f"👂 Transcribing locally...")
        
        # fp16=False prevents warnings on CPU-only machines
        result = model.transcribe(temp_filename, fp16=False)
        
        text = result["text"].strip()
        print(f"📝 Heard: '{text}'")
        
        # Cleanup
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

        return text

    except Exception as e:
        print(f"❌ Transcription Error: {e}")
        return ""