import socketio
import asyncio
import base64
 
from app.services.transcription import transcribe_audio
from app.services.rag_engine import generate_rag_response
 
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    max_http_buffer_size=20_000_000,  # allow bigger WAV payloads
)
 
socket_app = socketio.ASGIApp(sio)
 
user_tasks: dict[str, asyncio.Task] = {}

# MEMORY STORAGE
# Key: Session ID (sid), Value: List of tuples [("human", "msg"), ("ai", "msg")]
chat_histories = {}
 
 
def normalize_audio_bytes(data) -> bytes:
    """
    Accepts bytes, list of ints, base64, or dict and returns WAV bytes.
    """
    if data is None:
        return b""
 
    if isinstance(data, (bytes, bytearray)):
        return bytes(data)
 
    if isinstance(data, list):
        return bytes(data)
 
    if isinstance(data, dict):
        if "audio" in data:
            return normalize_audio_bytes(data["audio"])
        if len(data) == 1:
            return normalize_audio_bytes(next(iter(data.values())))
        return b""
 
    if isinstance(data, str):
        try:
            return base64.b64decode(data)
        except Exception:
            return b""
 
    return b""
 
 
@sio.event
async def connect(sid, environ):
    print(f"-- Client connected: {sid}")
    chat_histories[sid] = [] # Initialize empty memory for this user
    await sio.emit("server_status", {"msg": "Connection successful", "status": "online"}, room=sid)
 
 
@sio.event
async def disconnect(sid):
    print(f"-- Client disconnected: {sid}")
    await cancel_previous_task(sid)
    
    # Cleanup memory to prevent leaks
    if sid in chat_histories:
        del chat_histories[sid]
 
 
@sio.event
async def ping(sid, data):
    print(f"-- Received ping from {sid}: {data}")
    await sio.emit("pong", {"msg": "Server is alive!"}, room=sid)
 
 
async def cancel_previous_task(sid):
    task = user_tasks.get(sid)
    if task and not task.done():
        print(f"-- Interrupting previous task for {sid}...")
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            print(f"-- Task for {sid} cancelled.")
    user_tasks.pop(sid, None)
 
 
@sio.event
async def interrupt(sid, data=None):
    print(f"-- Interruption signal from {sid}")
    await cancel_previous_task(sid)
    await sio.emit("stop_audio", {}, room=sid)
 
 
async def process_user_audio(sid, wav_bytes: bytes):
    try:
        if not wav_bytes:
            await sio.emit("agent_response", {"text": "I didn't receive any audio."}, room=sid)
            return
 
        # Optional: Basic WAV header check
        if not (len(wav_bytes) >= 12 and wav_bytes[0:4] == b"RIFF"):
            print(f"-- Warning: Audio header might be invalid. Len: {len(wav_bytes)}")
 
        print(f"-- Audio bytes received for {sid}: {len(wav_bytes)}")
 
        # 1. Transcribe
        user_text = await asyncio.to_thread(transcribe_audio, wav_bytes)
 
        if not user_text:
            await sio.emit("agent_response", {"text": "I couldn't hear you clearly."}, room=sid)
            return
 
        print(f"-- Transcribed ({sid}): {user_text}")
 
        # 2. Get History
        history = chat_histories.get(sid, [])
 
        # 3. Generate Answer (Pass history to RAG)
        ai_answer = await generate_rag_response(user_text, history=history, group_type="B")
 
        # 4. Update History
        # We append the new turn and keep only the last 6 turns (3 back-and-forths) to save tokens
        history.append(("human", user_text))
        history.append(("ai", ai_answer))
        chat_histories[sid] = history[-6:]
 
        # 5. Respond
        await sio.emit("agent_response", {"text": ai_answer}, room=sid)
        print(f"-- Sent reply to {sid}")
 
    except asyncio.CancelledError:
        print(f"-- Task cancelled for {sid}")
        await sio.emit("stop_audio", {}, room=sid)
        raise
 
    except Exception as e:
        print(f"-- Error processing audio for {sid}: {e}")
        await sio.emit("agent_response", {"text": "Server error while processing audio."}, room=sid)
 
 
@sio.event
async def audio_stream(sid, data):
    wav_bytes = normalize_audio_bytes(data)
    print(f"🎤 Received audio_stream from {sid} ({len(wav_bytes)} bytes)")
 
    await cancel_previous_task(sid)
 
    task = asyncio.create_task(process_user_audio(sid, wav_bytes))
    user_tasks[sid] = task