import os
from pathlib import Path

from dotenv import load_dotenv


env_file = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_file)




embedding_model = OpenAIEmbeddings(
    model="openai/text-embedding-3-small",
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
)
