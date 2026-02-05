import os
import sys

# Adding the parent directory to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from langchain_community.document_loaders import TextLoader, PyPDFLoader, DirectoryLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings # <--- CHANGED
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
DATA_PATH = os.path.join("data", "documents")
DB_PATH = os.path.join("data", "chromadb")

def ingest_data():
    print(f"📂 Loading documents from: {DATA_PATH}")

    documents = []

    # Load docx files
    if any(f.endswith(".docx") for f in os.listdir(DATA_PATH)):
        print("   - Loading .docx files...")
        docx_loader = DirectoryLoader(DATA_PATH, glob="**/*.docx", loader_cls=Docx2txtLoader)
        documents.extend(docx_loader.load())

    # Load pdfs
    if any(f.endswith(".pdf") for f in os.listdir(DATA_PATH)):
        print("   - Loading .pdf files...")
        pdf_loader = DirectoryLoader(DATA_PATH, glob="**/*.pdf", loader_cls=PyPDFLoader)
        documents.extend(pdf_loader.load())

    # Load txt files
    if any(f.endswith(".txt") for f in os.listdir(DATA_PATH)):
        print("   - Loading .txt files...")
        txt_loader = DirectoryLoader(DATA_PATH, glob="**/*.txt", loader_cls=TextLoader)
        documents.extend(txt_loader.load())
    
    if not documents:
        print("--- No documents found. ---")
        return

    print(f"   Total found: {len(documents)} document(s).")

    # --- OPTIMIZATION FOR 10-PAGE DOCS ---
    # Larger chunks (1000 chars) with significant overlap (200 chars) ensures 
    # we capture full concepts/paragraphs, not just sentence fragments.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    
    print(f"--- Split into {len(chunks)} text chunks. ---")

    print("--- Generating Embeddings (Local - Nomic) ---")
    
    # Use the specialized embedding model we pulled earlier
    embedding_function = OllamaEmbeddings(model="nomic-embed-text")

    db = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function,
        persist_directory=DB_PATH
    )

    print("--- Success! Local Knowledge Base Built. ---")

if __name__ == "__main__":
    ingest_data()