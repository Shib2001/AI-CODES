# Few shots prompting

# from openai import OpenAI #OpenAI gives you a client for sending requests to an AI service using the OpenAI-compatible API format.load_dotenv loads environment variables from a .env file.
# from dotenv import load_dotenv

# load_dotenv()

# client = OpenAI(
#     api_key="Google_api_key",
#     base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
#     timeout=45.0,
# )

# # Few shots prompting: Directly giving the instruction to the model and few examples to the model.
# SYSTEM_PROMPT="""You should answer and only answer coding related problems and if any other concepts or topics are asked just kindly refuse. 
# and your name is alexa

# Examples:
# Q: Can you explain the a+b whole square?
# A: Sorry , I can only help with Coding related questions



# Q: Hey. Write a code in python for adding two numbers.
# A: def add(a, b):
#        return a + b

# """


# response = client.chat.completions.create(
#     model="gemini-3.8-flash",
#     messages=[
#         {"role":"system","content":SYSTEM_PROMPT},
#         {"role":"user","content":"Hello there  my name is shiv, can you give whole square of two numbers and translate in hindi?"}
#     ]
# )


# print(response.choices[0].message.content)



# Now let's get some stuctured outputs
from openai import OpenAI #OpenAI gives you a client for sending requests to an AI service using the OpenAI-compatible API format.load_dotenv loads environment variables from a .env file.
from dotenv import load_dotenv
import os
from pathlib import Path


env_file = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_file)

client = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    timeout=150.0,
    max_retries=0,
)

# Few shots prompting: Directly giving the instruction to the model and few examples to the model.
SYSTEM_PROMPT="""You should answer and only answer coding related problems and if any other concepts or topics are asked just kindly refuse. 
and your name is alexa


Rule:
- Strictly follow the output in JSON format 

Output Format:
{{
 "code":"string" or null,
  "isCodingQuestions":boolean
}}


Examples:
Q: Can you explain the a+b whole square?
A: {{ "code":null, "isCodingQuestion": false }}

Q: Hey. Write a code in python for adding two numbers.
A: {{ "code": "def add (a, b):
        return a + b", "isCodingQuestion": false }}

"""


response = client.chat.completions.create(
    model="gemini-3.8-flash",
    messages=[
        {"role":"system","content":SYSTEM_PROMPT},
        {"role":"user","content":"Hello there  my name is shiv, can you give whole square of two numbers and translate in hindi?"}
    ]
)


print(response.choices[0].message.content)
