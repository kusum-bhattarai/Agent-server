import os
import sys

# Adding the parent directory to the system path so we can import 'app' if needed
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from langchain_community.document_loaders import TextLoader, PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

# Verify API Key exists (Logic Check)
if not os.getenv("OPENAI_API_KEY"):
    print("❌ ERROR: OPENAI_API_KEY not found in .env file.")
    print("   The script will fail to generate embeddings without it.")
    # We continue just to show the logic flow, but it will crash at step 4
else:
    print("✅ API Key found.")

# --- CONFIGURATION ---
DATA_PATH = os.path.join("data", "documents")
DB_PATH = os.path.join("data", "chromadb")

def ingest_data():
    print(f"📂 Loading documents from: {DATA_PATH}")

    # This logic grabs all .txt and .pdf files in the folder
    loader = DirectoryLoader(DATA_PATH, glob="**/*.txt", loader_cls=TextLoader)
    # Note: change glob to "**/*.pdf" and loader_cls to PyPDFLoader for pdfs
    
    docs = loader.load()
    
    if not docs:
        print("⚠️ No documents found. Please add files to data/documents/")
        return

    print(f"   Found {len(docs)} document(s).")

    # Chunking the text into 500-character chunks with 50-character overlap to preserve some context
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = text_splitter.split_documents(docs)
    
    print(f"🧩 Split into {len(chunks)} text chunks.")

    print("🧠 Generating Embeddings and saving to ChromaDB...")
    
    # converting text to embeddings
    embedding_function = OpenAIEmbeddings()

    # create (or update) the db on disk
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function,
        persist_directory=DB_PATH
    )

    print("   The agent is now ready to retrieve this knowledge.")

if __name__ == "__main__":
    ingest_data()