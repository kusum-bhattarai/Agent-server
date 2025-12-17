import socketio
import time
import os

# Standard Socket.IO client
sio = socketio.Client()
SERVER_URL = 'http://0.0.0.0:8000'
AUDIO_FILE = 'test_audio.wav'  # Make sure this file exists!

@sio.event
def connect():
    print(f"✅ Connected to {SERVER_URL}")
    print(f"🎤 Sending audio file: {AUDIO_FILE}...")
    
    # 1. Load the audio bytes
    if not os.path.exists(AUDIO_FILE):
        print(f"❌ Error: {AUDIO_FILE} not found. Please record a test clip first.")
        sio.disconnect()
        return

    with open(AUDIO_FILE, 'rb') as f:
        audio_data = f.read()

    # 2. Emit the 'audio_stream' event
    # We send the raw bytes directly, just like Unity will.
    sio.emit('audio_stream', audio_data)

@sio.event
def agent_response(data):
    print("\n🗣️ AGENT RESPONSE:")
    print(f"   '{data.get('text')}'\n")
    sio.disconnect()

@sio.event
def disconnect():
    print("❌ Disconnected.")

if __name__ == "__main__":
    try:
        sio.connect(SERVER_URL)
        sio.wait()
    except Exception as e:
        print(f"Connection failed: {e}")