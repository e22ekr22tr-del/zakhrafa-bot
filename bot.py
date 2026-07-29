import telebot
import os
from flask import Flask
from threading import Thread

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    msg = """🤍 هلا بيك ! 
انا بوت الزخرفة التلقائي
اكتب اي اسم او كلمة واني ازخرفها الك فوراً

مثال: اكتب احمد
"""
    bot.reply_to(message, msg)

@bot.message_handler(func=lambda m: True)
def zakhrafa(message):
    text = message.text
    results = [
        f"♡ {text} ♡",
        f"◈ {text} ◈",
        f"✧ {text} ✧",
        f"★ {text} ★",
        f"〲 {text} 〲",
        f"『{text}』",
        f"۝ {text} ۝",
        f"々 {text} 々",
        f"╰‿╯ {text} ╰‿╯",
        f"꧁ {text} ꧂"
    ]
    msg = "🔥 الزخارف الجاهزة الك 🔥\n\n" + "\n".join(results)
    bot.reply_to(message, msg)

app = Flask('')
@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()
bot.polling()
