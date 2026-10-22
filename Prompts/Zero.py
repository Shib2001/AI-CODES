# Zero shot prompting : is giving the instructions directly 

from openai import OpenAI #OpenAI gives you a client for sending requests to an AI service using the OpenAI-compatible API format.load_dotenv loads environment variables from a .env file.
from dotenv import load_dotenv
from pathlib import Path

import os

env_file = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_file)

client = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    timeout=150.0,
    max_retries=0,
)


#zERO SHOT PROMPTING : GIVING INSTRUCTONS DICRECTLY TO THE MODEL
SYSTEM_PROMPT="You should answer and only answer coding related problems and if any other concepts or topics are asked just kindly refuse. and your name is alexa"


response = client.chat.completions.create(
    model="gemini-3.8-flash",
    messages=[
        {"role":"system","content":SYSTEM_PROMPT},
        {"role":"user","content":"Hello there  my name is shiv, what's your name"}
    ]
)

# response stores the result returned by the API.

# client.chat.completions.create() sends a request to generate a response.

# model specifies which AI model you want to use.

# messages contains the conversation you send to the model.

print(response.choices[0].message.content)


# Let's break it down:
# - response — the complete API response.
# - .choices — the list of generated response choices.
# - [0] — selects the first choice because Python indexing starts at zero.
# - .message — accesses the message in that choice.
# - .content — gets the actual text of the message.
# - print() — displays that text.