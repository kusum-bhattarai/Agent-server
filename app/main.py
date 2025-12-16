from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.socket_events import socket_app

# FASTAPI instance
app = FastAPI(title="Construction XR Agent Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Mount the Socket.IO App
# This tells FastAPI: "If a request comes to /socket.io, let the socket_app handle it."
app.mount("/socket.io", socket_app)

# 4. Basic HTTP Route (Health Check)
@app.get("/")
async def root():
    return {"message": "Agent Server is running", "status": "active"}

# 5. Entry Point
if __name__ == "__main__":
    # This block allows you to run the file directly via python app/main.py
    # However, we usually use the 'uvicorn' command in the terminal.
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)