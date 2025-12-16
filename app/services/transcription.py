import os
import io
import wave  
import openai
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI()

def transcribe_audio(audio_bytes):
    try:
        # Check if we need to convert Raw PCM to WAV
        # If the file header doesn't start with 'RIFF', it's likely raw PCM.
        if not audio_bytes.startswith(b'RIFF'):
            print("⚠️ Raw PCM detected. Wrapping in WAV header...")
            
            # Create a new buffer for the WAV file
            wav_buffer = io.BytesIO()
            
            # PARAMETERS: You MUST match what Magic Leap is sending.
            # Standard Unity mic capture is often:
            # Channels: 1 (Mono)
            # Sample Width: 2 (16-bit)
            # Frame Rate: 44100 or 48000 Hz
            CHANNELS = 1
            SAMPLE_WIDTH = 2 
            FRAME_RATE = 44100 
            
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(CHANNELS)
                wav_file.setsampwidth(SAMPLE_WIDTH)
                wav_file.setframerate(FRAME_RATE)
                wav_file.writeframes(audio_bytes)
            
            # Reset buffer position to start so OpenAI can read it
            wav_buffer.seek(0)
            audio_file = wav_buffer
            audio_file.name = "audio.wav"
            
        else:
            # It already has a WAV header
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