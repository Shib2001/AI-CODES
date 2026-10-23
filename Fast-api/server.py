from fastapi import FastAPI , Body
from ollama import Client

app = FastAPI()
Client = Client(
    host="http://localhost:11434",
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/Contact-us")
def read_root():
    return {"email":"piyushgarg.dev@gmail.com"}

@app.post("/chat")
def chat(
        message : str = Body(..., description="The Message")
):
    response = Client.chat(model="gemma:2b", messages=[
        {"role":"user", "content":message}
    ])

    return {"response": response.message.content}