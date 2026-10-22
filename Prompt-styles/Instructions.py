# Instruction prompting: tell the model what to do, then provide the input.
instruction = "Translate the sentence into French."
user_query = "Good morning."

# Llama 2 uses [INST] and [/INST] to mark the instruction.
prompt = f"[INST] {instruction}\n{user_query} [/INST]"
print(prompt)
