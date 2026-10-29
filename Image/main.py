import base64
import mimetypes
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

image_path = input("Image path: ")
image_type = mimetypes.guess_type(image_path)[0] or "image/jpeg"
image = base64.b64encode(Path(image_path).read_bytes()).decode("utf-8")

response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {os.getenv('OPEN_ROUTER')}"},
    json={
        "model": "google/gemma-4-26b-a4b-it:free",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{image_type};base64,{image}"},
                    },
                ],
            }
        ],
    },
)

response.raise_for_status()
print(response.json()["choices"][0]["message"]["content"])
