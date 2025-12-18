import os
import sys

# Adding the parent directory to the system path so we can import 'app' if needed
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from langchain_community.document_loaders import TextLoader, PyPDFLoader, DirectoryLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

# Verify API Key exists (Logic Check)
if not os.getenv("OPENAI_API_KEY"):
    print("--- ERROR: OPENAI_API_KEY not found in .env file. ---")
    print("   The script will fail to generate embeddings without it.")
    # We continue just to show the logic flow, but it will crash at step 4
else:
    print("✅ API Key found.")

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

    # Load pdfs for future use
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
        print("--- No documents found. Please add .docx, .pdf, or .txt files to data/documents/ ---")
        return

    print(f"   Total found: {len(documents)} document(s).")

    # Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = text_splitter.split_documents(documents)
    
    print(f"--- Split into {len(chunks)} text chunks. ---")

    print("--- Generating Embeddings and saving to ChromaDB ---")
    
    embedding_function = OpenAIEmbeddings()

    db = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function,
        persist_directory=DB_PATH
    )

    print("--- Success! The agent is now ready to retrieve this knowledge. ---")

if __name__ == "__main__":
    ingest_data()