from flask import Flask, request
import requests
import os
import traceback

app = Flask(__name__)

# === Load environment variables ===
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Debug to confirm tokens are loaded
print("🔍 TELEGRAM_TOKEN loaded:", TELEGRAM_TOKEN)
print("🔍 OPENAI_API_KEY loaded:", "✅ Loaded" if OPENAI_API_KEY else "❌ Missing")

# === Validate Telegram Token ===
if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN not found. Please set it in Render environment variables.")

# === Define webhook path ===
WEBHOOK_URL_PATH = f"/{TELEGRAM_TOKEN}"
print("🔍 Route registered for:", WEBHOOK_URL_PATH)


# === Helper: Send message back to Telegram ===
def send_message(chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        print("📤 Sending message:", payload)
        r = requests.post(url, json=payload)
        print("📨 Telegram response:", r.status_code, r.text)
    except Exception as e:
        print("❌ Error in send_message():", e)
        traceback.print_exc()


# === Helper: Ask ChatGPT (OpenAI API) ===
def ask_chatgpt(user_message):
    try:
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        data = {
            "model": "gpt-4o-mini",  # Fast, low-cost ChatGPT model
            "messages": [
                {"role": "system", "content": """
You are Outdoorzilla's multilingual customer service assistant.
Always reply in the same language as the customer.
If unsure or if the question is complex, politely suggest contacting a human representative.
"""},
                {"role": "user", "content": user_message}
            ]
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        print("✅ OpenAI API response:", response.status_code)
        if response.status_code != 200:
            print("❌ OpenAI error:", response.text)
            return "Sorry, I had trouble connecting to our AI system."

        return response.json()["choices"][0]["message"]["content"]

    except Exception as e:
        print("❌ Error in ask_chatgpt():", e)
        traceback.print_exc()
        return "Sorry, I encountered an error processing your request."


# === Telegram Webhook Route ===
@app.route(WEBHOOK_URL_PATH, methods=["POST"])
def telegram_webhook():
    try:
        data = request.get_json(force=True)
        print("📩 Received update:", data)

        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            user_text = data["message"]["text"]
            reply = ask_chatgpt(user_text)
            send_message(chat_id, reply)
        else:
            print("⚠️ No message text found in update.")

        return "OK", 200

    except Exception as e:
        print("❌ Error in telegram_webhook():", e)
        traceback.print_exc()
        return "Error", 500


# === Health check route ===
@app.route("/", methods=["GET"])
def home():
    return "✅ Outdoorzilla ChatGPT Bot is running!"


# === Start app ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

