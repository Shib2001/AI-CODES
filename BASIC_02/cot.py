# Chain of thought prompting

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

import json

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

message_history = [
    {"role":"system", "content": SYSTEM_PROMPT}
]

user_query = input("Enter your query: ")
message_history.append({"role":"user", "content": user_query})

while True:
    response = client.chat.completions.create(
        model="gemini-3.8-flash",
        response_format={"type": "json_object"},
        messages=message_history,
    )

    raw_result = response.choices[0].message.content
    message_history.append({"role":"assistant", "content": raw_result})
    parsed_result = json.loads(raw_result)

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
        {"role": "user", "content": "Write a code to add n numers in js"},
    ]
)

content = response.choices[0].message.content
if content:
    print(content)
else:
    print("Gemini returned an empty response.")