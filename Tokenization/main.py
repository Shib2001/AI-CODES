import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")

text = "What'sup bro how are you"

tokens = enc.encode(text)

#Tokens [45350, 817, 3714, 1495, 553, 481] ( we would get this in the reuslt)
print("Tokens", tokens)


decoded = enc.decode([45350, 817, 3714, 1495, 553, 481])
print("Decoded tokens:" , decoded)



# the whole flow is these #Tokens [45350, 817, 3714, 1495, 553, 481]  are passed to the llm , then the llm keeps predicting the next set of tokens
#then you decode the whole token array and give the result to the user