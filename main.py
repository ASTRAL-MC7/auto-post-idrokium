import os
import time
import random
import requests
import threading
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

app = Flask(__name__)

signatures = [
    "— @idrokium",
    "› @idrokium",
    ":: @idrokium",
    "⟡ @idrokium",
    "// @idrokium",
    "[idrokium]"
]

categories = [
    "wisdom",
    "question",
    "story",
    "creative",
    "news",
    "fact",
    "brain_teaser",
    "this_or_that",
    "challenge",
    "life_hack",
    "myth_fact"
]


def gemini_generate(prompt: str) -> str:
    if not GEMINI_API_KEY:
        return "Fikrlar jim emas, faqat bugun ular yozilmay qoldi."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    try:
        r = requests.post(url, json=payload, timeout=20)
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return "Bugun fikrlar biroz chalkash... lekin bu ham insoniy."


def build_prompt(category):
    return {
        "wisdom": "Write a deep philosophical quote with human tone.",
        "question": "Ask a psychological question that triggers comments.",
        "story": "Write a short strange micro-story with emotional depth.",
        "creative": "Write abstract human inner monologue style text.",
        "news": "Write neutral news-style text + ask opinion.",
        "fact": "Give an interesting science or psychology fact.",
        "brain_teaser": "Give a logic puzzle (no answer).",
        "this_or_that": "Create a 'This or That' choice question.",
        "challenge": "Give a 1-day self improvement challenge.",
        "life_hack": "Give a practical life hack.",
        "myth_fact": "State a myth and correct it briefly."
    }.get(category, "Write something meaningful.")


def send_to_telegram(text):
    try:
        requests.post(TELEGRAM_URL, json={
            "chat_id": CHANNEL_ID,
            "text": text
        }, timeout=10)
    except Exception as e:
        print("Telegram send error:", e)


def generate_post():
    category = random.choice(categories)
    prompt = build_prompt(category)

    content = gemini_generate(prompt)
    signature = random.choice(signatures)

    final_text = f"{content}\n\n{signature}"
    send_to_telegram(final_text)


# -------------------------
# ADMIN COMMAND HANDLER
# -------------------------
def handle_command(text, user_id):
    if user_id != ADMIN_ID:
        return

    if text == "/send":
        generate_post()


# -------------------------
# TELEGRAM WEBHOOK ROUTE
# -------------------------
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()

    if "message" in data:
        msg = data["message"]
        text = msg.get("text", "")
        user_id = msg["from"]["id"]

        handle_command(text, user_id)

    return "ok"


# -------------------------
# KEEP ALIVE + HOURLY LOOP
# -------------------------
def loop():
    while True:
        try:
            generate_post()
        except Exception as e:
            print("Loop error:", e)

        time.sleep(3600)


@app.route("/")
def home():
    return "idrokium bot is running."


# -------------------------
# START APP
# -------------------------
if __name__ == "__main__":
    threading.Thread(target=loop).start()

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
