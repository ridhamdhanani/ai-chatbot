from search import build_context
from llm import ask_llm

query = "Artificial Intelligence"

context = build_context(query)
response = ask_llm(query, context)

print("AI RESPONSE:\n")
print(response)