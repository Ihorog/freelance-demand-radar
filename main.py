import os
import sys
import telebot
import threading
from flask import Flask
from groq import Groq

# Ініціалізація веб-заглушки для Render
app = Flask(__name__)
@app.route('/')
def health_check():
    return "Legend ci is alive", 200

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

if not BOT_TOKEN or not GROQ_KEY:
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

def run_bot():
    try:
        bot.remove_webhook()
        print("[+] Cloud Bot is pooling...")
        bot.infinity_polling()
    except Exception as e:
        print(f"Bot Error: {e}")

if __name__ == "__main__":
    # Запускаємо бота в окремому потоці
    threading.Thread(target=run_bot, daemon=True).start()
    # Запускаємо веб-сервер на порту, який хоче Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
