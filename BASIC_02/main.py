# # Import the helper that reads values from a .env file.
# from dotenv import load_dotenv
# # Import Google's Generative AI library.
# from google import genai

# # Load GOOGLE_API_KEY from the .env file into the environment.
# load_dotenv()

# # Create the Google client; it reads GOOGLE_API_KEY automatically.
# client = genai.Client()

# # Send a prompt to Gemini and keep the response.
# interaction = client.interactions.create(
#     # Choose which Gemini model to use.
#     model="gemini-3.7-flash",
#     # Write your question or instruction as normal text here.
#     input="Hello gemini how are you , my name is shiv",
# )

# # Print the text Gemini returned.
# print(interaction.output_text)



import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

env_file = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_file)

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise SystemExit(
        f"GOOGLE_API_KEY is missing. Add GOOGLE_API_KEY=your_key to {env_file}."
    )

client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    timeout=45.0,
    max_retries=0,
)

print("Sending request to Gemini...", flush=True)
stream = client.chat.completions.create(
    model="gemini-3.8-flash",
    messages=[
        {"role": "system", "content":"You are an expert in the scienes only and only answer science related questions , and if someone asks anything other then kindly refuse them in hindi"},
        {"role":"user", "content":"Hey there , my name is shiv who are you, can you solve a maths problem"}
    ],
    stream=True,
)

for chunk in stream:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
print()