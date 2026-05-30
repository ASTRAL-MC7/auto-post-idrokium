import os
import requests
import random
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

app = Flask(__name__)

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

signatures = [
    "— @idrokium",
    "› @idrokium",
    ":: @idrokium",
    "⟡ @idrokium",
    "// @idrokium",
    "[idrokium]"
]


# -------------------------
# GEMINI AUTO-FALLBACK ENGINE
# -------------------------
def gemini_generate(prompt):
    # Multiple model candidates (safe fallback chain)
    endpoints = [
        "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent",
        "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent",
        "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent",
    ]

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    last_error = None

    for url in endpoints:
        try:
            full_url = f"{url}?key={GEMINI_API_KEY}"
            r = requests.post(full_url, json=payload, timeout=20)
            data = r.json()

            print("TRY:", url)
            print("RESPONSE:", data)

            if "error" in data:
                last_error = data["error"].get("message", "unknown error")
                continue

            return data["candidates"][0]["content"]["parts"][0]["text"], None

        except Exception as e:
            last_error = str(e)
            continue

    return None, last_error or "Unknown Gemini failure"


# -------------------------
# TELEGRAM SENDER
# -------------------------
def send_to_channel(text):
    try:
        requests.post(BASE_URL, json={
            "chat_id": CHANNEL_ID,
            "text": text
        }, timeout=10)
    except Exception as e:
        print("Telegram error:", e)


# -------------------------
# PROMPT ENGINE
# -------------------------
def build_prompt():
    prompts = [
        "Write a deep philosophical thought that feels human and slightly emotional.",
        "Ask a psychological question that makes people comment deeply.",
        "Write a short mysterious micro-story with meaning.",
        "Write an abstract inner monologue of a human mind.",
        "Create a life insight that feels raw and real."
    ]
    return random.choice(prompts)


# -------------------------
# MAIN POST LOGIC
# -------------------------
def generate_and_send():
    prompt = build_prompt()

    content, error = gemini_generate(prompt)

    if error:
        message = f"⚠️ GEMINI API ERROR\n\n{error}"
    else:
        message = f"{content}\n\n{random.choice(signatures)}"

    send_to_channel(message)


# -------------------------
# ADMIN COMMAND HANDLER
# -------------------------
def handle_command(text, user_id):
    if user_id != ADMIN_ID:
        return

    if text == "/send":
        generate_and_send()


# -------------------------
# WEBHOOK ROUTE
# -------------------------
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)

    if not data:
        return "ok"

    msg = data.get("message", {})
    text = msg.get("text", "")
    user_id = msg.get("from", {}).get("id")

    handle_command(text, user_id)

    return "ok"


# -------------------------
# HEALTH CHECK
# -------------------------
@app.route("/")
def home():
    return "idrokium bot running"


# -------------------------
# START SERVER
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
