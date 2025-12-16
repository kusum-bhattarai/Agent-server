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

async def generate_rag_response(query_text: str, group_type: str = "B"):
    """
    The Main Logic (Async Version):
    """
    try:
        retriever, llm = get_rag_chain()
        
        # Retrieve relevant documents (Async)
        # Note: retrievers might not have ainvoke in older versions, 
        # but modern LangChain supports async retrieval.
        # If this fails, wrap it in asyncio.to_thread, but usually it's fine.
        docs = await retriever.ainvoke(query_text)
        context_text = "\n\n".join([doc.page_content for doc in docs])

        prompt_template = ChatPromptTemplate.from_template("""
        You are an expert Construction Safety Officer and NEC Code Specialist.
        CONTEXT FROM MANUALS: {context}
        USER QUESTION: {question}
        INSTRUCTIONS:
        - Answer based ONLY on the provided context.
        - Concise (under 3 sentences).
        - Group {group}.
        """)

        # Chain
        chain = prompt_template | llm
        
        # Use 'ainvoke' instead of 'invoke'
        response = await chain.ainvoke({
            "context": context_text,
            "question": query_text,
            "group": group_type
        })

        return response.content

    except Exception as e:
        print(f"❌ RAG Error: {e}")
        return "I'm having trouble accessing my safety manuals right now."