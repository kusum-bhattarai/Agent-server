import socketio

from app.services.transcription import transcribe_audio
from app.services.rag_engine import generate_rag_response

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

# This wraps the socket server so FastAPI can mount it later.
socket_app = socketio.ASGIApp(sio)

# --- EVENT LISTENERS ---

@sio.event
async def connect(sid, environ):
    """
    Triggered automatically when Unity connects.
    'sid' is the unique Session ID for that specific user.
    """
    print(f"✅ Client connected: {sid}")
    
    # Send a welcome message back to the client
    await sio.emit('server_status', {'msg': 'Connection successful', 'status': 'online'}, room=sid)

@sio.event
async def disconnect(sid):
    """
    Triggered when the client closes the app or loses internet.
    """
    print(f"❌ Client disconnected: {sid}")

@sio.event
async def ping(sid, data):
    """
    A simple test event. 
    If Unity sends 'ping', we reply with 'pong'.
    """
    print(f"📩 Received ping from {sid}: {data}")
    await sio.emit('pong', {'msg': 'Server is alive!'}, room=sid)

@sio.event
async def audio_stream(sid, data):
    """
    Event: 'audio_stream'
    Input: Raw bytes (WAV data) from Unity Microphone.
    Logic: Audio -> Text -> RAG -> Answer -> Client
    """
    print(f"🎤 Received audio stream from {sid}")
    
    # 1. Transcribe (The Ears)
    # 'data' here is expected to be the raw byte array
    user_text = transcribe_audio(data)
    
    if not user_text:
        await sio.emit('agent_response', {'text': "I couldn't hear you clearly."}, room=sid)
        return

    # 2. Process (The Brain)
    # We reuse the logic we built in Step 1
    ai_answer = generate_rag_response(user_text, group_type="B")

    # 3. Respond (The Voice)
    await sio.emit('agent_response', {'text': ai_answer}, room=sid)
    print(f"📤 Sent reply: {ai_answer}")