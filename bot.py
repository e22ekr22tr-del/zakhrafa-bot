import telebot
import os
import json
import time
import traceback
from threading import Thread
from flask import Flask

API_KEY = os.environ.get("BOT_TOKEN")  
UserBot = "Tik_TokLBOT" 
ADMIN = 1076477010 

bot = telebot.TeleBot(API_KEY, parse_mode="Markdown")

DB_FILE = "hamsa.json"
MEMB_FILE = "memb.txt"
BLOCK_FILE = "blocklist.txt"

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"pending": {}, "hamsas": {}}

def read_file(f):
    return open(f, encoding='utf-8').read().strip() if os.path.exists(f) else ""

def filterName(name):
    scam = ['[','*',']','_','(',')','`']
    for s in scam: name = name.replace(s, '')
    return name

for f in [DB_FILE, MEMB_FILE, BLOCK_FILE]:
    if not os.path.exists(f): 
        if f == DB_FILE: save_db({"pending": {}, "hamsas": {}})
        else: open(f, 'w', encoding='utf-8').close()

WELCOME_MSG = """
🌹 **اهلاً وسهلاً بك في بوت الهمسات السريه** 🌹
📮 **انا بوت ارسل همساتك السريه بدون ما احد يعرف** 
🧸 **كل الي عليك ترد على رسالة الشخص ودز** `همسة`

👑 **المطور:** [المحامي احمد علي](tg://user?id=1076477010)
"""

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    from_id = message.from_user.id
    text = message.text
    
    memb = read_file(MEMB_FILE).splitlines()
    if str(from_id) not in memb:
        with open(MEMB_FILE, "a", encoding='utf-8') as f: f.write(f"{from_id}\n")
    
    block = read_file(BLOCK_FILE).splitlines()
    if str(from_id) in block:
        bot.send_message(chat_id, "⛳| عزي انت محظور من البوت")
        return
    
    db = load_db()
    if text.startswith("/start hamsa"):
        if str(from_id) in db["pending"]:
            bot.send_message(chat_id, "*⤾حسناً ارسل الهمسة الآن 🧸♥️*")
            db["pending"][str(from_id)]['state'] = 'send'
            save_db(db)
        else:
            bot.send_message(chat_id, "⚠️ لا توجد همسة بانتظارك")
        return
        
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("➕ ضفني لمجموعتك", url=f"https://t.me/{UserBot}?startgroup=true"))
    try:
        bot.send_photo(chat_id, photo=ADMIN, caption=WELCOME_MSG, reply_markup=markup)
    except:
        bot.send_message(chat_id, WELCOME_MSG, reply_markup=markup)

@bot.message_handler(func=lambda m: m.text and m.text.strip() in ["همسه", "همسة", "اهمس", "أهمس"])
def hamsa_reply(message):
    if message.chat.type == "private": return
    if not message.reply_to_message: 
        bot.reply_to(message, "❌ رد على رسالة الشخص الي تريد تدزله همسة")
        return
    if message.reply_to_message.from_user.is_bot: 
        bot.reply_to(message, "😒 لا يمكنك عمل همسة لبوت")
        return
    if message.reply_to_message.from_user.id == message.from_user.id:
        bot.reply_to(message, "😒 لا يمكنك عمل همسة لنفسك")
        return
    
    from_id = message.from_user.id
    to_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id
    reply_id = message.reply_to_message.message_id
    
    db = load_db()
    hamsa_id = str(int(time.time()))
    
    db["pending"][str(from_id)] = {
        'chat_id': chat_id,
        'to': to_id,
        'reply_msg_id': reply_id,
        'hamsa_id': hamsa_id,
        'state': 'waiting'
    }
    save_db(db)
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("❤️ قم بارسال الهمسه بـ الخاص", url=f"https://t.me/{UserBot}?start=hamsa"))
    bot.reply_to(message, "*اهلا بك يمكنك الضغط على الزر وإرسال الهمسة في ⤾خاص البوت 🧸♥️*", reply_markup=markup)

@bot.message_handler(func=lambda m: str(m.from_user.id) in load_db()["pending"] and load_db()["pending"][str(m.from_user.id)].get('state') == 'send')
def get_hamsa_text(message):
    from_id = message.from_user.id
    text = message.text
    db = load_db()
    if str(from_id) not in db["pending"]: return
    data = db["pending"][str(from_id)]
    
    bot.send_message(message.chat.id, "*⤾ . تم ارسال الهمسة بنجاح 🥳✅*")
    
    # نحفظ الهمسة ونترك الـ pending
    db["hamsas"][data['hamsa_id']] = {
        'text': text,
        'from': from_id,
        'to': data['to']
    }
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("🧧 فتح الهمسـه", callback_data=f"o&{data['hamsa_id']}"),
        telebot.types.InlineKeyboardButton("🚫 حذف", callback_data=f"d&{data['hamsa_id']}")
    )
    
    bot.send_message(
        data['chat_id'],
        f"*⤾ . ؏ــمرري 🧸♥️ لديك همسة من*\n[{filterName(message.from_user.first_name)}](tg://user?id={from_id})",
        reply_to_message_id=data['reply_msg_id'],
        reply_markup=markup
    )
    
    del db["pending"][str(from_id)]
    save_db(db)

@bot.callback_query_handler(func=lambda call: call.data.startswith("o&"))
def open_hamsa(call):
    _, hamsa_id = call.data.split("&")
    db = load_db()
    data = db["hamsas"].get(hamsa_id)
    
    if not data: 
        bot.answer_callback_query(call.id, "❌ الهمسة منتهية او محذوفة", show_alert=True)
        return
    
    from_id = data['from']
    to_id = data['to']
    text = data['text']
    from_id2 = call.from_user.id

    if from_id2 == to_id or from_id2 == from_id:
        bot.answer_callback_query(call.id, f"💌 الهمسة:\n\n{text}", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "🔒 الهمسة ليست لك", show_alert=True)
        bot.send_message(from_id, f"*⚠️ لقد حاول هذا الشخص كشف همستك*\n\n*الشخص:* [{filterName(call.from_user.first_name)}](tg://user?id={from_id2})")

@bot.callback_query_handler(func=lambda call: call.data.startswith("d&"))
def del_hamsa(call):
    _, hamsa_id = call.data.split("&")
    db = load_db()
    data = db["hamsas"].get(hamsa_id)
    if not data: return
    
    if call.from_user.id == data['from']:
        if hamsa_id in db["hamsas"]:
            del db["hamsas"][hamsa_id]
            save_db(db)
        bot.delete_message(call.message.chat.id, call.message_id)
        bot.answer_callback_query(call.id, "✅ تم حذف الهمسة")
    else:
        bot.answer_callback_query(call.id, "لحذف الهمسة يجب أن تكون انت من ارسل هذه الهمسة", show_alert=True)

app = Flask('')
@app.route('/')
def home(): return "Bot is running!"
def run(): app.run(host='0.0.0.0', port=8080)
Thread(target=run).start()

print("Bot Started...")
bot.infinity_polling()
