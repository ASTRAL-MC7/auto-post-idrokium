import os
import random
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

app = Flask(__name__)

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

signatures = [
    "— @idrokium",
    "› @idrokium",
    ":: @idrokium",
    "⟡ @idrokium",
    "// @idrokium",
    "[idrokium]"
]


# -------------------------
# GEMINI (FIXED FOR YOUR MODEL LIST)
# -------------------------
def gemini_generate(prompt):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    try:
        r = requests.post(url, json=payload, timeout=20)
        data = r.json()

        print("GEMINI RESPONSE:", data)

        if "error" in data:
            return None, data["error"].get("message", "Unknown Gemini error")

        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return text, None

    except Exception as e:
        return None, str(e)


# -------------------------
# CONTENT PROMPT ENGINE
# -------------------------
def build_prompt():
    prompts = [
        "Write a deep philosophical thought that feels human and slightly emotional.",
        "Ask a psychological question that makes people comment deeply.",
        "Write a short mysterious micro-story.",
        "Write an abstract human inner monologue.",
        "Create a life insight that feels raw and real.",
        "Write something slightly dark but meaningful about human behavior."
    ]
    return random.choice(prompts)


# -------------------------
# TELEGRAM SEND
# -------------------------
def send_to_channel(text):
    try:
        requests.post(TELEGRAM_URL, json={
            "chat_id": CHANNEL_ID,
            "text": text
        }, timeout=10)
    except Exception as e:
        print("Telegram error:", e)


# -------------------------
# MAIN POST FUNCTION
# -------------------------
def generate_post():
    content, error = gemini_generate(build_prompt())

    if error:
        message = f"⚠️ GEMINI API ERROR:\n{error}"
    else:
        message = f"{content}\n\n{random.choice(signatures)}"

    send_to_channel(message)


# -------------------------
# ADMIN COMMAND (/send)
# -------------------------
def handle_command(text, user_id):
    if user_id != ADMIN_ID:
        return

    if text == "/send":
        generate_post()


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
# START
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
