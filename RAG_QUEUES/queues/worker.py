import os
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
from openai import OpenAI

env_file = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_file)

api_key = os.getenv("OPEN_ROUTER")
if not api_key:
    raise RuntimeError("OPEN_ROUTER is not set in the project .env file.")

openrouter_client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
)


embedding_model = OpenAIEmbeddings(
    model="openai/text-embedding-3-small",
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
)


vector_db = QdrantVectorStore.from_existing_collection(
    embedding=embedding_model,
    url="http://localhost:6333",
    collection_name="learning-rag"
)


def process_query(query: str) -> str:
    print("Searching Chunks", query)
    search_results = vector_db.similarity_search(query=query)

    context = "\n\n\n".join(
        f"Page Content: {result.page_content}\n"
        f"Page Number: {result.metadata['page_label']}\n"
        f"File Location: {result.metadata['source']}"
        for result in search_results
    )

    system_prompt = f"""
You are a helpful AI assistant. Answer the user's question using only the
context retrieved from the PDF. Include the relevant page number so the user
can find the information in the source.

Context:
{context}
"""

    response = openrouter_client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
    )

    answer = response.choices[0].message.content
    if answer is None:
        raise RuntimeError("OpenRouter returned an empty response.")

    print(f"AI RESPONSE: {answer}")
    return answer
