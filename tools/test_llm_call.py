from utils.local_llm import call_llm

prompt = "Say hello in French."
result = call_llm(prompt)
print(result)
