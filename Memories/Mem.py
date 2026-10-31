from mem0 import Memory
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import json


env_file = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_file)

api_key = os.getenv("OPEN_ROUTER")
if not api_key:
    raise RuntimeError("OPEN_ROUTER is not set in the project .env file.")

openrouter_base_url = "https://openrouter.ai/api/v1"

client = OpenAI(
    api_key=api_key,
    base_url=openrouter_base_url,
)

config = {
    "version": "v1.1",
    "embedder": {
        "provider": "openai",
        "config": {
            "api_key": api_key,
            "openai_base_url": openrouter_base_url,
            "model": "openai/text-embedding-3-small",
        },
    },
    "llm": {
        "provider": "openai",
        "config": {
            "api_key": api_key,
            "openai_base_url": openrouter_base_url,
            "model": "openai/gpt-4o",
        },
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
        }
    },
}

mem_client = Memory.from_config(config)


while True:
    user_query = input("Ask something : ")
    # Now let's get the context from the memory based on the user query
    search_memory = mem_client.search(
        query=user_query,
        filters={"user_id": "default_user"},
        top_k=3,
    )

    memories = [
        f"ID: {mem.get('id')}\nMemory: {mem.get("memory")}" 
        for mem in search_memory.get("results", [])
    ]
    print("Retrieved Memories:", json.dumps(memories, indent=2))


    SYSTEM_PROMPT = f"""
     here is the context of the user : {json.dumps(memories, indent=2)}


"""

    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {"role": "user", "content": user_query}
        ]
    )

    ai_response = response.choices[0].message.content
    print("AI Response:", ai_response)

    # Now this conversation is stored in the memory and we can retrieve it later for context
    mem_client.add(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query},
        ],
        user_id="default_user",
    )

    print("Conversation stored in memory. You can retrieve it later for context.")