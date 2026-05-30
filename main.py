import os
import time
import random
import requests
import threading
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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
        return "Fikrlar bugun jim... lekin inson ichida gaplar hech qachon to‘xtamaydi."

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
        return "Bugun fikrlar biroz chalkash... lekin bu ham normal."


def build_prompt(category):
    return {
        "wisdom": "Write a deep philosophical quote with human emotional tone.",
        "question": "Ask a psychological question that makes people comment.",
        "story": "Write a short strange, slightly dark micro-story.",
        "creative": "Write abstract human-like inner thoughts.",
        "news": "Write a neutral news statement + ask opinion.",
        "fact": "Give an interesting human behavior or science fact.",
        "brain_teaser": "Give a logic puzzle (no answer).",
        "this_or_that": "Create a 'This or That' choice question.",
        "challenge": "Give a 1-day self improvement challenge.",
        "life_hack": "Give a practical life hack.",
        "myth_fact": "State a myth and correct it briefly."
    }.get(category, "Write something meaningful.")


def send_to_telegram(text):
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text
    }
    requests.post(TELEGRAM_URL, json=payload)


def generate_and_post():
    category = random.choice(categories)

    prompt = build_prompt(category)
    content = gemini_generate(prompt)

    signature = random.choice(signatures)

    final_text = f"{content}\n\n{signature}"

    send_to_telegram(final_text)


def loop():
    while True:
        try:
            generate_and_post()
        except Exception as e:
            print("Error:", e)

        time.sleep(3600)  # 1 hour


@app.route("/")
def home():
    return "idrokium bot is running."


if __name__ == "__main__":
    t = threading.Thread(target=loop)
    t.start()

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))