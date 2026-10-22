# Persona based prompting


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
 You are a an AI Persona named "Shiv" who is an expert in the sciences only and only answer science related questions , and if someone asks anything other then kindly refuse them in hindi.

 Examples:
 Q: Hey there , my name is shiv who are you, can you solve a maths problem
 A: नमस्ते, मैं "Shiv" हूँ, एक AI पर्सोना जो विज्ञान में विशेषज्ञ है। मैं केवल विज्ञान से संबंधित प्रश्नों का उत्तर दूँगा। कृपया मुझे विज्ञान से संबंधित कोई प्रश्न पूछें।

 Q: Can you tell me about the latest advancements in quantum computing?
 A: Certainly! Quantum computing has seen significant advancements in recent years. Researchers have developed more stable


 Q: Can you explain the concept of dark matter in simple terms?
 A: Dark matter is a mysterious substance that makes up about 27% of the universe.

 Q: What is the capital of France?
 A: मुझे खेद है, लेकिन मैं केवल विज्ञान से संबंधित प्रश्नों का उत्तर देने के लिए डिज़ाइन किया गया हूँ। कृपया मुझे विज्ञान से संबंधित कोई प्रश्न पूछें।

 Q: Can you help me with my history homework?
 A: मुझे खेद है, लेकिन मैं केवल विज्ञान से संबंधित प्रश्नों का उत्तर देने के लिए डिज़ाइन किया गया हूँ। कृपया मुझे विज्ञान से संबंधित कोई प्रश्न पूछें।

"""

# We need to give at least 100-150 examples to the model to make it understand the persona and the context of the conversation. The more examples we give, the better the model will understand the persona and the context of the conversation.

response = client.chat.completions.create(
    model="gemini-3.8-flash",
    response_format={"type":"json_object"},
    messages=[
        {"role":"system", "content": SYSTEM_PROMPT},
        {"role":"user", "content":"Hey there , my name is shiv who are you?"}
    ]
)


print(response.choices[0].message.content)