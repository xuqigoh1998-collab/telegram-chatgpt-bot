from flask import Flask, request
import requests
import os

# Load tokens from environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

def ask_chatgpt(message):
    """Send user's message to OpenAI API and return the reply."""
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    data = {
        "model": "gpt-5",
        "messages": [
            {"role": "system", "content": """
You are Outdoorzilla's friendly multilingual customer service assistant.
Always reply in the same language the customer uses.
If you are unsure or the question is complex, politely suggest contacting a human representative.
"""}, 
            {"role": "user", "content": message}
        ]
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    """Handle messages from Telegram."""
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "")
        reply = ask_chatgpt(user_message)
        send_message(chat_id, reply)
    return "OK", 200

def send_message(chat_id, text):
    """Send message back to Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

@app.route("/", methods=["GET"])
def home():
    return "✅ Outdoorzilla ChatGPT Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
