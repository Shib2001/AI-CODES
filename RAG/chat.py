import os
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
from openai import OpenAI

env_file = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_file)

api_key = os.getenv("OPEN_ROUTER")
if not api_key:
    raise RuntimeError("OPEN_ROUTER is not set in the project .env file.")

openrouter_client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
)


# Vector embeddings
embedding_model = OpenAIEmbeddings(
    model="openai/text-embedding-3-small",
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
)

# we wrote the existing collection because this time we don't want to store anything we just have to get the data from the existing collection
vector_db = QdrantVectorStore.from_existing_collection(
    embedding=embedding_model,
    url="http://localhost:6333",
    collection_name="learning-rag"
)


# Take user input 

user_query = input("Ask something : ")

# Now we are tell the vector db to do the similarity search and it will return only the relevant chunks to me 

search_results = vector_db.similarity_search(query=user_query)

context = "\n\n\n".join([
    f"Page Content: {result.page_content}\nPage Number: {result.metadata['page_label']}\nFile Location: {result.metadata['source']}"
    for result in search_results
])


SYSTEM_PROMPT = f"""
  You are a helpful AI assistant who answeres user query based on the available context retrieved from a PDF
  file along with page_contents and page number.

  You should only answer the user based on the following context and navigate the 
  user to open the right page number to know more.

  Context:{context}

"""

response = openrouter_client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]
)

print(f"Here is your AI response: {response.choices[0].message.content}")