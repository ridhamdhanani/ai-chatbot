from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse

from db import create_user, get_user, save_message, load_messages
from auth import hash_password, verify_password, create_token, decode_token
from search import build_context
from llm import stream_chat, should_search, generate_title

import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@app.get("/")
def serve_ui():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))


# 🔐 REGISTER
@app.post("/register")
def register(data: dict):
    username = data["username"]
    password = hash_password(data["password"])

    if not create_user(username, password):
        raise HTTPException(status_code=400, detail="User exists")

    return {"status": "ok"}


# 🔐 LOGIN
@app.post("/login")
def login(data: dict):
    username = data["username"]
    password = data["password"]

    user = get_user(username)
    if not user or not verify_password(password, user[0]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(username)
    return {"token": token}


# 💬 CHAT (SSE STREAMING)
@app.get("/chat")
def chat(q: str, session_id: str, token: str):

    username = decode_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Unauthorized")

    history = load_messages(username, session_id)

    title = None
    if len(history) == 0:
        title = generate_title(q)

    save_message(username, session_id, "user", q)
    history.append({"role": "user", "content": q})

    context = build_context(q) if should_search(q) else None

    def event_stream():
        stream = stream_chat(history, context)
        full = ""

        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                full += delta
                yield f"data: {delta}\n\n"

        save_message(username, session_id, "assistant", full)

    headers = {
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no"
    }

    if title:
        safe_title = title.encode("ascii", "ignore").decode()
        headers["X-Chat-Title"] = safe_title

    return StreamingResponse(event_stream(), media_type="text/event-stream", headers=headers)