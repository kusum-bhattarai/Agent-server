import os
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
DB_PATH = os.path.join("data", "chromadb")

def get_rag_chain():
    """
    Initializes the connection to the Vector DB and the LLM.
    """
    embedding_function = OpenAIEmbeddings()

    vector_db = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embedding_function
    )

    # find the top 3 most relevant documents
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})

    # We use temperature=0.3 to keep answers factual but natural.
    llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

    return retriever, llm

def generate_rag_response(query_text: str, group_type: str = "B"):
    """
    The Main Logic:
    1. Search DB for context.
    2. Construct a prompt.
    3. Ask GPT-4 for the answer.
    """
    try:
        # Initialize resources
        retriever, llm = get_rag_chain()
        
        # Retrieve relevant documents
        docs = retriever.invoke(query_text)
        context_text = "\n\n".join([doc.page_content for doc in docs])

        # System prompt with instructions
        prompt_template = ChatPromptTemplate.from_template("""
        You are an expert Construction Safety Officer and NEC Code Specialist.
        
        CONTEXT FROM MANUALS:
        {context}
        
        USER QUESTION:
        {question}
        
        INSTRUCTIONS:
        - Answer based ONLY on the provided context if possible.
        - If the user asks about a safety violation, cite the specific code (e.g., NEC 210.8).
        - Keep the answer concise (under 3 sentences) suitable for a HoloLens/Magic Leap display.
        - The user is in Group {group}. If Group == 'A', be passive. If Group == 'B', be active and warning.
        """)

        # 3. Send to GPT-4
        chain = prompt_template | llm
        response = chain.invoke({
            "context": context_text,
            "question": query_text,
            "group": group_type
        })

        return response.content

    except Exception as e:
        print(f"❌ RAG Error: {e}")
        # Fallback if DB is missing or API key is invalid
        return "I'm having trouble accessing my safety manuals right now."