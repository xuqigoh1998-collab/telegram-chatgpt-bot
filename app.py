from flask import Flask, request
import requests
import os
import traceback

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def ask_chatgpt(message):
    try:
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        data = {
            "model": "gpt-4o-mini",  # use this model name for API access
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
        print("✅ OpenAI API response:", response.status_code)
        print(response.text)
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("❌ Error in ask_chatgpt():", e)
        traceback.print_exc()
        return "Sorry, I encountered an error while processing your message."

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    try:
        data = request.get_json()
        print("📩 Received update:", data)

        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            user_message = data["message"].get("text", "")
            reply = ask_chatgpt(user_message)
            send_message(chat_id, reply)

        return "OK", 200

    except Exception as e:
        print("❌ Error in telegram_webhook():", e)
        traceback.print_exc()
        return "Error", 500

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    print("📤 Sending message:", payload)
    r = requests.post(url, json=payload)
    print("Telegram response:", r.status_code, r.text)

@app.route("/", methods=["GET"])
def home():
    return "✅ Outdoorzilla ChatGPT Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
