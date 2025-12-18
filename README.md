# Agent-server
Construction Safety AI Agent ServerThis is the Python backend for an XR/AR Construction Safety application. It serves as an intelligent voice agent that answers questions about safety regulations (OSHA) and NEC codes using RAG (Retrieval-Augmented Generation).

## Features
- Real-time Audio Streaming: Receives raw audio (WAV) from a Unity client via Socket.IO.
- Speech-to-Text: Transcribes audio using OpenAI Whisper.
- RAG Engine: Retrieves answers from a custom knowledge base (ChromaDB) built from construction manuals.
- Document Support: Ingests .docx, .pdf, and .txt files automatically.
- Async Processing: Handles multiple user connections and interruptions smoothly.

## Tech Stack
- Language: Python 3.10+
- Framework: Python-SocketIO (ASGI)
- AI/LLM: LangChain, OpenAI GPT-4o, OpenAI Embeddings
- Vector DB: ChromaDB
- Transcription: OpenAI Whisper API

## Installation
1. Clone the Repository and 
```bash
git clone https://github.com/kusum-bhattarai/Agent-server
cd Agent-server
```
2. Set up Virtual Environment (Recommended)
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

3. Install Dependencies
```bash
pip install -r requirements.txt
```
4. Configure Environment
Create a file named .env in the root directory and add your OpenAI API key:
```Ini, TOML
OPENAI_API_KEY=sk-proj-12345...
```
## Knowledge Base Setup
The agent needs to "learn" the safety manuals before it can answer questions. 
1. Add Documents: Place your .docx, .pdf, or .txt files into the data/documents/ folder.
- *Tip*: For best results with .docx files, separate topics with double line breaks. 
2. Build the Brain: Run the ingestion script to chunk and index the data.
```bash
python ingest_pdfs.py
```
- Output: You should see ✅ Success! The agent is now ready...

## Running the Server
Start the Socket.IO server using Uvicorn:
```bash
uvicorn app.main:app --host 0.0.0.0 --reload
```
The server is now listening at http://localhost:8000.

