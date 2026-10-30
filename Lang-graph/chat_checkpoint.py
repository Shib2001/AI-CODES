from typing_extensions import TypedDict  # TypedDict se graph state ke fields aur unke types define hote hain.
from typing import Annotated  # Annotated se type ke saath extra behavior ya metadata jod sakte hain.
from langgraph.graph.message import add_messages  # add_messages purane aur naye messages ko merge karta hai.
from langgraph.graph import StateGraph, START, END  # StateGraph workflow banata hai; START aur END uske entry/exit points hain.
from langchain.chat_models import init_chat_model  # init_chat_model provider ke hisaab se chat model initialize karta hai.
import os  # Environment variables se secrets aur configuration padhne ke liye.
from pathlib import Path  # .env file ka absolute path banane ke liye.
from dotenv import load_dotenv  # .env file ki values ko environment mein load karta hai.
from langgraph.checkpoint.mongodb import MongoDBSaver  # MongoDBSaver graph ke checkpoints MongoDB mein store karta hai.

env_file = Path(__file__).resolve().parent.parent / ".env"  # Script se ek folder upar project root ki .env file ka path banata hai.
load_dotenv(env_file)  # Project root wali .env file ko environment variables mein load karta hai.

api_key = os.getenv("OPEN_ROUTER")  # .env se OpenRouter API key read karta hai.
if not api_key:  # Agar API key missing ya empty hai to...
    raise RuntimeError("OPEN_ROUTER is not set in the project .env file.")  # ...clear error dekar execution rokta hai.

llm = init_chat_model(  # OpenRouter ke OpenAI-compatible endpoint par chat model configure karta hai.
    model="openai/gpt-4o-mini",  # OpenRouter par use hone wale model ka naam set karta hai.
    model_provider="openai",  # LangChain ko OpenAI-compatible provider use karne ko batata hai.
    api_key=api_key,  # Loaded OpenRouter key model client ko deta hai.
    base_url="https://openrouter.ai/api/v1",  # Requests ko OpenRouter API endpoint par bhejta hai.
    max_tokens=1024,  # Model ke response ko adhiktam 1024 tokens tak limit karta hai.
)  # Model configuration yahan complete hoti hai.


class State(TypedDict):  # Graph ke andar pass hone wale state ka structure define karta hai.
    messages: Annotated[list, add_messages]  # Messages field mein naye messages ko purane messages ke saath jodta hai.


def chatbot(state: State):  # Chatbot node current graph state ko input ke roop mein leta hai.
    response = llm.invoke(state.get("messages"))  # State ke messages model ko bhejkar jawab leta hai.
    return {"messages": [response]}  # Model ka jawab messages field mein graph ko wapas deta hai.


graph_builder = StateGraph(State)  # State schema ke saath graph builder initialize karta hai.
graph_builder.add_node("chatbot", chatbot)  # chatbot function ko graph ke chatbot node ke roop mein register karta hai.
graph_builder.add_edge(START, "chatbot")  # Graph shuru hote hi chatbot node chalata hai.
graph_builder.add_edge("chatbot", END)  # Chatbot node ke baad graph ko khatam karta hai.

db_uri = os.getenv(  # Environment se MongoDB URI leta hai; value na mile to local Compose credentials use karta hai.
    "MONGODB_URI",  # .env mein set kiya ja sakne wala MongoDB connection variable.
    "mongodb://admin:admin@localhost:27017/?authSource=admin",  # Compose ke local MongoDB ke liye default URI.
)  # MongoDB URI selection yahan complete hota hai.
config = {"configurable": {"thread_id": "Shiv"}}  # Checkpoint ko is conversation thread ke saath associate karta hai.

with MongoDBSaver.from_conn_string(db_uri, db_name="lg") as checkpointer:  # MongoDB checkpoint saver kholta hai; db_name checkpoint database hai.
    graph_with_checkpointer = graph_builder.compile(checkpointer=checkpointer)  # Isi saver ke saath checkpoint-enabled graph compile karta hai.
    for chunk in graph_with_checkpointer.stream(  # Saver khula rakhte hue stream ke har state snapshot par loop chalata hai.
        {"messages": ["Hello, what do i love to play and what is my name what is my favourite food ?"]},  # Graph ko shuruaati user message deta hai.
        config=config,  # Stream call ko thread ID deta hai, jisse checkpoints sahi conversation mein save hote hain.
        stream_mode="values",  # Har event par poora updated graph state stream karta hai.
    ):  # Stream loop ka body yahan se shuru hota hai.
        chunk["messages"][-1].pretty_print()  # Snapshot ka aakhri message, yani naya response, print karta hai.


