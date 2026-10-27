import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

env_file = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_file)

client = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    timeout=150.0,
    max_retries=0,
)

def get_weather(city):
    url = f"https://wttr.in/{city}?format=%C+%t+%w"
    # Note: This is a simplified example. In a real application, you would need to handle the HTTP request and response properly.
    response = requests.get(url)
    if response.status_code == 200:
        return f"The weather in {city} is: {response.text}"
    else:
        return "Could not retrieve weather information."


def main():
    user_input = input("Ask a science question: ")
    response = client.chat.completions.create(
        model="gemini-3.8-flash",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ],
    )
    print("Response:", response.choices[0].message.content)

print(get_weather("Noida"))