import telebot
import os
import json
import time
from threading import Thread
from flask import Flask

API_KEY = os.environ.get("BOT_TOKEN")  
UserBot = "Tik_TokLBOT" # معرف بوتك
IdBot = "2119941952"
ADMIN = 1076477010 # حط ايدك هنا

bot = telebot.TeleBot(API_KEY, parse_mode="Markdown")

# ====== دوال مساعدة ======
def save(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

def load(file):
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def read_file(f):
    return open(f, encoding='utf-8').read().strip() if os.path.exists(f) else ""

def filterName(name):
    scam = ['[','*',']','_','(',')','`']
    for s in scam: name = name.replace(s, '')
    return name

# انشاء الملفات اذا مو موجودة
if not os.path.exists("hamsa.json"): save("hamsa.json", {})
if not os.path.exists("memb.txt"): open("memb.txt", 'w', encoding='utf-8').close()
if not os.path.exists("blocklist.txt"): open("blocklist.txt", 'w', encoding='utf-8').close()

# رسالة الترحيب الفخمة
WELCOME_MSG = """
🌹 **اهلاً وسهلاً بك في بوت الهمسات السريه** 🌹

📮 **انا بوت ارسل همساتك السريه بدون ما احد يعرف** 
🧸 **كل الي عليك ترد على رسالة الشخص ودز** `همسة`

**طريقة الاستخدام:**
1.  رد على رسالة الشخص
2.  اكتب `همسة` 
3.  اضغط الزر وراح يحولك للخاص
4.  ارسل الهمسة وراح توصل اله سريه

🔒 **الهمسة يشوفها بس المرسل والمستلم**
"""

# ====== /start ======
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    from_id = message.from_user.id
    name = filterName(message.from_user.first_name)
    text = message.text

    memb = read_file("memb.txt").splitlines()
    if str(from_id) not in memb:
        with open("memb.txt", "a", encoding='utf-8') as f: f.write(f"{from_id}\n")
    
    block = read_file("blocklist.txt").splitlines()
    if str(from_id) in block:
        bot.send_message(chat_id, "⛳| عزيزي انت محظور من البوت")
        return
    
    h = load("hamsa.json")

    if text.startswith("/start hamsa"):
        if str(from_id) in h and h[str(from_id)].get('state') == 'waiting':
            bot.send_message(chat_id, "*⤾حسناً ارسل الهمسة الآن 🧸♥️*")
            h[str(from_id)]['state'] = 'send'
            save("hamsa.json", h)
        else:
            bot.send_message(chat_id, "⚠️ لا توجد همسة بانتظارك")
        return
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("➕ ضفني لمجموعتك", url=f"https://t.me/{UserBot}?startgroup=true"))
    bot.send_message(chat_id, WELCOME_MSG, reply_markup=markup)

# ====== لوحة الادمن ======
@bot.message_handler(commands=['admin'])
def admin(message):
    if message.from_user.id != ADMIN: return
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("📊 احصائيات الاعضاء", callback_data="mem"))
    markup.add(telebot.types.InlineKeyboardButton("📢 الاذاعه", callback_data="bcc"))
    bot.send_message(message.chat.id, f"👑 اهلا بك مطوري {filterName(message.from_user.first_name)}", reply_markup=markup)

# ====== نظام الهمسة ======
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
    
    h = load("hamsa.json")
    h[str(from_id)] = {
        'chat_id': chat_id,
        'to': to_id,
        'reply_msg_id': message.reply_to_message.message_id,
        'state': 'waiting'
    }
    save("hamsa.json", h)
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("❤️ قم بارسال الهمسه بـ الخاص", url=f"https://t.me/{UserBot}?start=hamsa"))
    bot.reply_to(message, "*اهلا بك يمكنك الضغط على الزر وإرسال الهمسة في ⤾خاص البوت 🧸♥️*", reply_markup=markup)

@bot.message_handler(func=lambda m: str(m.from_user.id) in load("hamsa.json") and load("hamsa.json")[str(m.from_user.id)].get('state') == 'send')
def get_hamsa_text(message):
    from_id = message.from_user.id
    text = message.text
    h = load("hamsa.json")
    if str(from_id) not in h: return
    data = h[str(from_id)]
    
    bot.send_message(message.chat.id, "*⤾ . تم ارسال الهمسة بنجاح 🥳✅*")
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("🧧 فتح الهمسـه", callback_data=f"open&{data['to']}&{from_id}"),
        telebot.types.InlineKeyboardButton("🚫 حذف", callback_data=f"del#{from_id}")
    )
    
    msg = bot.send_message(
        data['chat_id'],
        f"*⤾ . ؏ــمرري 🧸♥️ لديك همسة من*\n[{filterName(message.from_user.first_name)}](tg://user?id={from_id})",
        reply_to_message_id=data['reply_msg_id'],
        reply_markup=markup
    )
    
    h[f"msg_{msg.message_id}"] = text
    save("hamsa.json", h)
    del h[str(from_id)]
    save("hamsa.json", h)

# ====== فتح الهمسة ======
@bot.callback_query_handler(func=lambda call: call.data.startswith("open&"))
def open_hamsa(call):
    _, to_id, from_id = call.data.split("&")
    to_id, from_id = int(to_id), int(from_id)
    from_id2 = call.from_user.id
    
    h = load("hamsa.json")
    text = h.get(f"msg_{call.message_id}")
    
    if not text: 
        bot.answer_callback_query(call.id, "❌ الهمسة منتهية او محذوفة", show_alert=True)
        return
    
    if from_id2 == to_id or from_id2 == from_id:
        bot.answer_callback_query(call.id, f"💌 الهمسة:\n\n{text}", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "🔒 الهمسة ليست لك", show_alert=True)
        bot.send_message(from_id, f"*⚠️ لقد حاول هذا الشخص كشف همستك*\n\n*الشخص:* [{filterName(call.from_user.first_name)}](tg://user?id={from_id2})")

# ====== حذف الهمسة ======
@bot.callback_query_handler(func=lambda call: call.data.startswith("del#"))
def del_hamsa(call):
    from_id = int(call.data.split("#")[1])
    if call.from_user.id == from_id:
        bot.delete_message(call.message.chat.id, call.message_id)
        h = load("hamsa.json")
        if f"msg_{call.message_id}" in h:
            del h[f"msg_{call.message_id}"]
            save("hamsa.json", h)
    else:
        bot.answer_callback_query(call.id, "لحذف الهمسة يجب أن تكون انت من ارسل هذه الهمسة", show_alert=True)

# ====== احصائيات ======
@bot.callback_query_handler(func=lambda call: call.data == "mem" and call.from_user.id == ADMIN)
def mem(call):
    memb = read_file("memb.txt").splitlines()
    band = read_file("blocklist.txt").splitlines()
    bot.edit_message_text(f"*📟 احصـائيات البـوت:\n\n👥 المشتركين: {len(memb)}\n🚫 المحظورين: {len(band)}*", call.message.chat.id, call.message_id)

# ====== تشغيل Flask + Bot ======
app = Flask('')
@app.route('/')
def home(): return "Bot is running!"

def run(): app.run(host='0.0.0.0', port=8080)
Thread(target=run).start()

print("Bot Started...")
bot.infinity_polling()
