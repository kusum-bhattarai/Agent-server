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

async def generate_rag_response(query_text: str, history: list = None, group_type: str = "B"):
    """
    The Main Logic (Async Version):
    - Now accepts 'history' to support follow-up questions.
    """
    try:
        retriever, llm = get_rag_chain()
        
        # 1. Format History for the Prompt
        # Converts list of tuples [('human', 'hi'), ('ai', 'hello')] into a text block
        history_text = ""
        if history:
            for role, text in history:
                history_text += f"{role.upper()}: {text}\n"
        
        # 2. Retrieve relevant documents
        docs = await retriever.ainvoke(query_text)
        context_text = "\n\n".join([doc.page_content for doc in docs])

        # 3. Updated Prompt with History
        prompt_template = ChatPromptTemplate.from_template("""
        You are an expert Construction Safety Officer and NEC Code Specialist.
        
        PREVIOUS CONVERSATION:
        {history}

        CONTEXT FROM MANUALS: {context}
        
        CURRENT USER QUESTION: {question}
        
        INSTRUCTIONS:
        - Answer based ONLY on the provided context and conversation history.
        - If the user asks a follow-up question (like "what about for high voltage?"), use the Previous Conversation to understand context.
        - Concise (under 3 sentences).
        - Group {group}.
        """)

        # Chain
        chain = prompt_template | llm
        
        response = await chain.ainvoke({
            "context": context_text,
            "question": query_text,
            "history": history_text,  # Pass the formatted history string
            "group": group_type
        })

        return response.content

    except Exception as e:
        print(f"-- RAG Error: {e}")
        return "I'm having trouble accessing my safety manuals right now."