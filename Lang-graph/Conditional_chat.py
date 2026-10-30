# Here we are gonna implement the conditional chat workflow 

from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Optional , Literal
from langgraph.graph import StateGraph,START, END
from openai import OpenAI

load_dotenv()

client = OpenAI()

class State(TypedDict):
    user_query: str
    llm_output: Optional[str]
    is_good: Optional[bool]


def chatbot(state:State):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role":"user", "content": state.get("user_query")}
        ]
    )

    state["llm_output"] = response.choices[0].message.content # here in the llm output we have appeneded the output we would got from the 
    return state

def endnode(state:State):
    return state

# So below we have implemented another node that would be used for the evaluation , that is the response to good enough for it to end 
# or we have to redirect it to another llm 


def evaluate_response(state: State) -> Literal["chatbot_gemini", "endnode"]:
    if True:
        return "endnode"

    return "chatbot_gemini"


def chatbot_gemini(state:State):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role":"user", "content": state.get("user_query")}
        ]
    )


graph_builder = StateGraph(State)


# let's register nodes

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("chabot_gemini", chatbot_gemini)
graph_builder.add_node("endnode", endnode)


# Now let's implement the edge cases 

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", evaluate_response)

graph_builder.add_edge("chatbot_gemini", "endnode")
graph_builder.add_edge("endnode", END)


# let's compile it 

graph = graph_builder.compile()

updated_state = graph.invoke(State({"user_query":"Hey what is 2+2?"}))
print(updated_state)
