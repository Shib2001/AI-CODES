# Chain of thought prompting

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

import json


# it is used to go to the parent directory of the current file and then load the .env file from there. This is useful for loading environment variables, such as API keys, that are stored in a .env file located in the parent directory of the script.
env_file = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_file)

client = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    timeout=150.0,
    max_retries=0,
)




SYSTEM_PROMPT = """
       
       You are an expert AI assistant in resolvung user queries using chain of thought 
       You work on START , PLAN and OUTPUT steps.
       You need to first PLAN what needs to be done. The PLAN can be multiple steps.
       Once you think eneough PLAN has been done , finally you can give an OUTPUT.


       Rules:
       - Strictly follow the given json output format 
       - Only run one step at a time.
       - The sequence of steps is START (where user gives and input), PLAN (That can be multiple times)
         and finally OUTPUT ( which is going to be displayed to the user).

        OUTPUT JSON FORM:
        {"step": "START| "PLAN" | "OUTPUT", "content": "Your content here"}

        Example:
        START: {"step": "START", "content": "Write a code to add n numbers in js"}
        PLAN: {"step": "PLAN", "content": "First I will create a function that takes n as input, then I will use a loop to add numbers from 1 to n, and finally return the sum."}
        PLAN: {"step": "PLAN", "content": "I will use a for loop to iterate from 1 to n and keep adding the numbers to a sum variable."}
        PLAN : {"step": "PLAN", "content": "I will return the sum variable after the loop ends."}
        PLAN: {"step": "PLAN", "content": "I will write the code in JavaScript syntax."}
        PLAN: {"step": "PLAN", "content": "I will test the function with a sample input to ensure it works correctly."}
        OUTPUT: {"step": "OUTPUT", "content": "Here is the JavaScript code to add n numbers:\n\nfunction addNumbers(n) {\n    let sum = 0;\n    for (let i = 1; i <= n; i++) {\n        sum += i;\n    }\n    return sum;\n}\n\n// Example usage:\nconsole.log(addNumbers(5)); // Output: 15"}



"""

# This creates the message list sent to the model. The system message contains the instructions above. 
# The list will also hold the user’s question and the model’s replies. basically this will contain the entire history 
# of all queries and responses in the current session. This is important for maintaining context in a conversation with the model.

message_history = [
    {"role":"system", "content": SYSTEM_PROMPT}
]

#The script prompts you to type a question, then adds it to the conversation as a user message
#The input() function displays a prompt and waits for the user to type something.
# and that user query is appeneded to the message_history list as a dictionary with the role "user" and the content being the user’s input.

user_query = input("Enter your query: ")
message_history.append({"role":"user", "content": user_query})


# Because True never becomes false, this loop continues indefinitely unless something stops it.

# Your program uses while True because it doesn't know in advance how many planning steps the model will produce.

# Maybe it returns two PLAN messages. Maybe it returns five. You want to continue until it produces OUTPUT.

# That is why you use a loop whose stopping condition is determined by a response from the model.



# This calls the API using the client's chat-completions interface.

# Let's examine each argument.
# Argument	                        Meaning
# model	                 The model identifier requested from the API
# response_format	        Requests JSON-object output
# messages	          The conversation and instructions sent to the model

while True:
    response = client.chat.completions.create(
        model="gemini-3.8-flash",
        response_format={"type": "json_object"},
        messages=message_history,
    )

    raw_result = response.choices[0].message.content # Take the text generated in the first response choice and store it in raw_result.
      #This adds the generated response to the conversation history.
      # Why is the role "assistant"? Because the message came from the AI model.
      # Why store raw_result instead of the parsed dictionary?
      # Because the chat API expects message content as text. A JSON string is still a string, so it can be sent back as the assistant's message content.
    message_history.append({"role":"assistant", "content": raw_result}) 
    parsed_result = json.loads(raw_result) #raw_result is text returned by the model. json.loads() converts that JSON-formatted text into a Python object—here, a dictionary—so the script can access its fields.

    if parsed_result.get("step") == "START":
        print("Starting the process...", parsed_result.get("content"))
        continue
    if parsed_result.get("step") == "PLAN":
        print("Planning step:", parsed_result.get("content"))
        continue
    if parsed_result.get("step") == "OUTPUT":
        print("Final output:", parsed_result.get("content"))
        break

print("Sending request to Gemini...", flush=True)
response = client.chat.completions.create(
    model="gemini-3.7-flash",
    response_format={"type": "json_object"},
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Hey there , my name is shiv who are you, can you solve a maths problem"},
    ]
)

content = response.choices[0].message.content
# response is the result returned by the API request.
# .choices is the list of replies the API returned.
# [0] selects the first reply (Python lists start at index 0).
# .message gets that reply’s message.
# .content gets the text of the message.
if content:
    print(content)
else:
    print("Gemini returned an empty response.")