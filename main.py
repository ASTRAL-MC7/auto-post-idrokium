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

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

app = Flask(__name__)

signatures = [
    "— @idrokium",
    "› @idrokium",
    ":: @idrokium",
    "⟡ @idrokium",
    "// @idrokium",
    "[idrokium]"
]


# -------------------------
# GEMINI TEST FUNCTION
# -------------------------
def gemini_generate(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    try:
        r = requests.post(url, json=payload, timeout=20)
        data = r.json()

        # DEBUG PRINT (Render logs)
        print("GEMINI RESPONSE:", data)

        if "error" in data:
            return None, f"API ERROR: {data['error'].get('message', 'unknown')}"

        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return text, None

    except Exception as e:
        return None, str(e)


# -------------------------
# SEND TO TELEGRAM
# -------------------------
def send_to_channel(text):
    try:
        requests.post(BASE_URL, json={
            "chat_id": CHANNEL_ID,
            "text": text
        })
    except Exception as e:
        print("Telegram error:", e)


# -------------------------
# SIMPLE PROMPT
# -------------------------
def build_prompt():
    return "Write a deep, human-like philosophical thought or question that makes people think."


# -------------------------
# MAIN POST LOGIC
# -------------------------
def generate_and_send():
    content, error = gemini_generate(build_prompt())

    if error:
        msg = f"⚠️ GEMINI API PROBLEM\n\nReason: {error}"
    else:
        msg = f"{content}\n\n{random.choice(signatures)}"

    send_to_channel(msg)


# -------------------------
# HANDLE COMMANDS
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
# HOME ROUTE
# -------------------------
@app.route("/")
def home():
    return "idrokium bot running"


# -------------------------
# START
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
