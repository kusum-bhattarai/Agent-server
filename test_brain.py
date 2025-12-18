import asyncio
from app.services.rag_engine import generate_rag_response

# Change this question to something specific from your Word doc
question = "How does water affect electricity?" 

async def main():
    print(f"🤖 Asking: {question}...")
    answer = await generate_rag_response(question)
    print(f"💡 Answer: {answer}")

if __name__ == "__main__":
    asyncio.run(main())