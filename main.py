import os
import time
import random
import requests
import secrets
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

last_message = ""

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


def send_message(text, chat_id):
    try:
        requests.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": text
        }, timeout=10)
    except Exception as e:
        print("Telegram error:", e)


def gemini_generate(prompt):
    if not GEMINI_API_KEY:
        return "API KEY YO‘Q"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "temperature": 1.3,
            "topP": 0.95
        }
    }

    try:
        r = requests.post(url, json=payload, timeout=20)
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("Gemini error:", e)
        return "Bugun fikrlar ishlamay qoldi..."


def build_prompt(category):
    return {
        "wisdom": "Write a deep philosophical quote with human tone.",
        "question": "Ask a psychological question that makes people comment.",
        "story": "Write a short strange emotional micro-story.",
        "creative": "Write abstract human inner monologue style text.",
        "news": "Write neutral news + ask opinion.",
        "fact": "Give an interesting science or psychology fact.",
        "brain_teaser": "Give a logic puzzle (no answer).",
        "this_or_that": "Create a 'This or That' choice question.",
        "challenge": "Give a 1-day self improvement challenge.",
        "life_hack": "Give a practical life hack.",
        "myth_fact": "State a myth and correct it briefly."
    }[category]


def generate_post():
    global last_message

    category = secrets.choice(categories)
    prompt = build_prompt(category)

    content = gemini_generate(prompt)
    signature = random.choice(signatures)

    final_text = f"{content}\n\n{signature}"

    # prevent exact repetition
    if final_text == last_message:
        return

    last_message = final_text

    send_message(final_text, CHANNEL_ID)


def handle_command(text, user_id):
    if user_id != ADMIN_ID:
        return

    if text == "/send":
        generate_post()


def poll_updates():
    offset = 0

    while True:
        try:
            r = requests.get(f"{BASE_URL}/getUpdates", params={
                "offset": offset,
                "timeout": 30
            }, timeout=35)

            data = r.json()

            for update in data.get("result", []):
                offset = update["update_id"] + 1

                msg = update.get("message")
                if not msg:
                    continue

                text = msg.get("text", "")
                user_id = msg["from"]["id"]

                handle_command(text, user_id)

        except Exception as e:
            print("Poll error:", e)

        time.sleep(1)


def hourly_post_loop():
    while True:
        try:
            generate_post()
        except Exception as e:
            print("Post loop error:", e)

        time.sleep(3600)


if __name__ == "__main__":
    import threading

    threading.Thread(target=poll_updates).start()
    hourly_post_loop()
