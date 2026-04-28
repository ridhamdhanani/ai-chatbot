from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def should_search(query: str) -> bool:
    """Decide if web search is needed"""
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Answer YES or NO. Should this query use web search?"},
            {"role": "user", "content": query}
        ],
        temperature=0
    )

    return "YES" in response.choices[0].message.content.upper()


def generate_title(user_message: str):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Generate a short 3-5 word title."},
            {"role": "user", "content": user_message}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()


def stream_chat(history, context: str | None):
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."}
    ]

    messages.extend(history)

    if context:
        messages.append({"role": "system", "content": f"Context:\n{context}"})

    return client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        stream=True,
        temperature=0.5
    )