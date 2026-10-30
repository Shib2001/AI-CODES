from typing_extensions import TypedDict  # TypedDict se state ka structure/type define hota hai.
from typing import Annotated  # Annotated type ke saath extra metadata attach karta hai.
from langgraph.graph.message import add_messages  # Message updates ko purani message list ke saath merge karta hai.
from langgraph.graph import StateGraph, START, END  # StateGraph se LangGraph workflow ka graph banate hain.


class State(TypedDict):  # Graph state mein kaun-se fields honge, yeh define karta hai.
    messages: Annotated[list, add_messages]  # Messages ki list : , also yaha pr jo add_messages ke jo annotation h wo use honge to append the message into the original "state", which we have done exactly below

# Now let's make some nodes which are basically functions 

def chatbot(state: State): # as i said state changes hote rhenge so for that we have defined the state here
    print("Inside the chatbot node", state)
    return {"messages":["Hi, This is a message from chatbot Node"]} # ab ye jo bhi maine return kiya h it will be append inot the original "state"

def sameplenode(state:State):
    print("Inside the  samplenode", state)
    return{"messages":["Hi, This is a messages from chatbot node another samplenode "]}


graph_builder = StateGraph(State)  # State schema use karke graph builder banata hai; nodes/edges baad mein add honge.

# Now let's register a node in the graph 

graph_builder.add_node("xyz", chatbot) # here xyz is the name of the node and the chatbot is the code 
graph_builder.add_node("samplenode", sameplenode)


# Now let's implement the edges

graph_builder.add_edge(START, "chatbot") # so here definded START to go to the chatbot node
graph_builder.add_edge("chatbot", "samplenode") # then from chatbot we have gone to the samplenode
graph_builder.add_edge("samplenode", END) # AND FROM samplenode we have end it .

# finally let's compile and make the graph ready 

graph = graph_builder.compile()

# Now let's test it 