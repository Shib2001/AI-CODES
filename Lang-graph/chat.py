from typing_extensions import TypedDict  # TypedDict se state ka structure/type define hota hai.
from typing import Annotated  # Annotated type ke saath extra metadata attach karta hai.
from langgraph.graph.message import add_messages  # Message updates ko purani message list ke saath merge karta hai.
from langgraph.graph import StateGraph, START, END  # StateGraph se LangGraph workflow ka graph banate hain.
from langchain.chat_models import init_chat_model
import os
from pathlib import Path
from dotenv import load_dotenv

env_file = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_file)

api_key = os.getenv("OPEN_ROUTER")
if not api_key:
    raise RuntimeError("OPEN_ROUTER is not set in the project .env file.")

llm = init_chat_model(
    model="openai/gpt-4o-mini",
    model_provider="openai",
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
    max_tokens=1024,
)


class State(TypedDict):  # Graph state mein kaun-se fields honge, yeh define karta hai.
    messages: Annotated[list, add_messages]  # Messages ki list : , also yaha pr jo add_messages ke jo annotation h wo use honge to append the message into the original "state", which we have done exactly below

# Now let's make some nodes which are basically functions 

def chatbot(state: State): # as i said state changes hote rhenge so for that we have defined the state here
    response = llm.invoke(state.get("messages"))
    return {"messages":[response]} # ab ye jo bhi maine return kiya h it will be append inot the original "state"

def sameplenode(state:State):
    print("\n\nInside the  samplenode", state)
    return{"messages":["Hi, This is a messages from chatbot node another samplenode "]}


graph_builder = StateGraph(State)  # State schema use karke graph builder banata hai; nodes/edges baad mein add honge.

# Now let's register a node in the graph 

graph_builder.add_node("chatbot", chatbot) # here xyz is the name of the node and the chatbot is the code 
graph_builder.add_node("samplenode", sameplenode)


# Now let's implement the edges

graph_builder.add_edge(START, "chatbot") # so here definded START to go to the chatbot node
graph_builder.add_edge("chatbot", "samplenode") # then from chatbot we have gone to the samplenode
graph_builder.add_edge("samplenode", END) # AND FROM samplenode we have end it .

# finally let's compile and make the graph ready 

graph = graph_builder.compile()

# Now let's test it , below we are invoking a graph and in the initiliased state we have added a message , and saved it into the updated state

updated_state = graph.invoke(State({"messages":["Hi, My name is shiv kumar jha"]}))
print("updated_state", updated_state)
