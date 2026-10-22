instruction = "Answer the question simply."
user_query = "What is 2 + 2?"

prompt = f"""### Instruction:
{instruction}

### Input:
{user_query}

### Response:"""

print(prompt)
