from transformers import pipeline

pipe = pipeline("image-text-to-text", model="google/gemma3-4b-it")



messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "image", "url": "https://images.unsplash.com/photo-1682685790910-1e3f5c7b8d4e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170&q=80",
                "type": "text", "text": "Describe the image in detail."
            }
        ]
    }
]

pipe(text=messages)