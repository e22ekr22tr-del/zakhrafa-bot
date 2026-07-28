import telebot
import os
from flask import Flask
from threading import Thread

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "هلا بيك! بوت الزخرفة جاهز 👑\nارسل اي اسم وازخرفه الك")

@bot.message_handler(func=lambda m: True)
def zakhrafa(message):
    text = message.text
    results = [
        f"❀ {text} ❀",
        f"۝ {text} ۝", 
        f"✧ {text} ✧",
        f"⋆ {text} ⋆"
    ]
    msg = "\n".join(results)
    bot.reply_to(message, msg)

app = Flask('')
@app.route('/')
def home():
    return "Bot is running!"
def run():
  app.run(host='0.0.0.0',port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()
bot.polling()
