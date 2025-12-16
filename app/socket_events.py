import socketio
import asyncio

from app.services.transcription import transcribe_audio
from app.services.rag_engine import generate_rag_response

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

# This wraps the socket server so FastAPI can mount it later.
socket_app = socketio.ASGIApp(sio)

# Dictionary to store the current running task for each user
# Format: { 'session_id': asyncio.Task }
user_tasks = {}

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

async def process_user_audio(sid, audio_data):
    """
    The actual logic for processing audio.
    We wrap this in a function so we can run it as a cancellable Task.
    """
    try:
        # 1. Transcribe (Blocking but fast enough, or make async if needed)
        # Note: Ideally run this in a thread executor if it takes >1s
        user_text = await asyncio.to_thread(transcribe_audio, audio_data)
        
        if not user_text:
            await sio.emit('agent_response', {'text': "I couldn't hear you clearly."}, room=sid)
            return

        print(f"📝 Transcribed ({sid}): {user_text}")

        # 2. Process (The Brain) - Now Async!
        ai_answer = await generate_rag_response(user_text, group_type="B")

        # 3. Respond
        await sio.emit('agent_response', {'text': ai_answer}, room=sid)
        print(f"📤 Sent reply to {sid}")

    except asyncio.CancelledError:
        print(f"🔇 Task cancelled for {sid} (User interrupted)")
        # Optionally tell Unity to stop playing any queued audio
        await sio.emit('stop_audio', {}, room=sid)
        raise # Re-raise to ensure proper task cleanup

@sio.event
async def audio_stream(sid, data):
    """
    Event: 'audio_stream'
    Expected behavior: Unity sends this when silence is detected (user finished sentence).
    """
    print(f"🎤 Received audio stream from {sid}")

    # 1. If the bot was already thinking/talking, STOP it first.
    await cancel_previous_task(sid)

    # 2. Start the new processing task
    task = asyncio.create_task(process_user_audio(sid, data))
    
    # 3. Save the task so we can interrupt it later
    user_tasks[sid] = task

async def cancel_previous_task(sid):
    """
    Cancels any ongoing RAG/processing task for this user.
    """
    if sid in user_tasks:
        task = user_tasks[sid]
        if not task.done():
            print(f"🛑 Interrupting previous task for {sid}...")
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                print(f"✅ Task for {sid} cancelled successfully.")
        # Remove from dict
        del user_tasks[sid]

@sio.event
async def interrupt(sid, data=None):
    """
    Unity calls this event immediately when it detects the user starts speaking.
    """
    print(f"✋ Interruption signal from {sid}")
    await cancel_previous_task(sid)