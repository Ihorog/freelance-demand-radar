import os
import sys
import telebot
import threading
import time
from flask import Flask
from groq import Groq

# 1. Веб-заглушка для Render (Має стартувати миттєво)
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Legend ci is operational", 200

# 2. Логіка Бота
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

def run_bot_logic():
    # Даємо веб-серверу 5 секунд, щоб Render його зафіксував
    time.sleep(5)
    try:
        print("[+] Спроба очищення вебхука...")
        bot.remove_webhook()
        print("[+] Запуск infinity_polling...")
        bot.infinity_polling(timeout=20, long_polling_timeout=20)
    except Exception as e:
        print(f"[!] Помилка бота: {e}")

if __name__ == "__main__":
    # Запускаємо бота в окремому потоці, щоб він не блокував Flask
    bot_thread = threading.Thread(target=run_bot_logic, daemon=True)
    bot_thread.start()

    # Запускаємо веб-сервер на порту 10000 (стандарт Render)
    port = int(os.environ.get("PORT", 10000))
    print(f"[+] Веб-сервер активовано на порту {port}")
    app.run(host='0.0.0.0', port=port)
