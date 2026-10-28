import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore


env_file = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_file)

api_key = os.getenv("OPEN_ROUTER")
if not api_key:
    raise RuntimeError("OPEN_ROUTER is not set in the project .env file.")

pdf_path = Path(__file__).parent / "dummy.pdf"



# Load this file


loader = PyPDFLoader(file_path=pdf_path)
docs = loader.load()
print(docs[0])


# Split each page into chunks, preferring natural text breaks.
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # Maximum characters in each chunk.
    chunk_overlap=400,  # Characters shared by neighboring chunks.
)

# Create smaller documents from docs; each keeps its page metadata.
chunks = text_splitter.split_documents(documents=docs)



# Now we need to create vector embeddings for these chunks 

embedding_model = OpenAIEmbeddings(
    model="openai/text-embedding-3-small",
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
)


vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embedding_model,
    url="http://localhost:6333",
    collection_name="learning-rag",
)

print("Indexing of documents done")


# Now that the indexing part is done we will go on to the retreival part and we will write that 
# chat.py


