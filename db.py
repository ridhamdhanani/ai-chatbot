import sqlite3

conn = sqlite3.connect("chat.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS chats (
    username TEXT,
    session_id TEXT,
    role TEXT,
    message TEXT
)
""")

conn.commit()


def create_user(username, password):
    try:
        cursor.execute("INSERT INTO users VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except:
        return False


def get_user(username):
    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    return cursor.fetchone()


def save_message(username, session_id, role, message):
    cursor.execute(
        "INSERT INTO chats VALUES (?, ?, ?, ?)",
        (username, session_id, role, message)
    )
    conn.commit()


def load_messages(username, session_id):
    cursor.execute(
        "SELECT role, message FROM chats WHERE username=? AND session_id=?",
        (username, session_id)
    )
    return [{"role": r, "content": m} for r, m in cursor.fetchall()]