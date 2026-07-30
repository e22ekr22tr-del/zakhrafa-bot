import telebot
import os
import json
from threading import Thread
from flask import Flask

API_KEY = os.environ.get("BOT_TOKEN")  # نحطه بمتغيرات Railway
UserBot = "zzll_bot" # غيره لمعرف بوتك بدون @
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

# ====== /start ======
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    from_id = message.from_user.id
    name = filterName(message.from_user.first_name)
    text = message.text

    # حفظ العضو
    memb = read_file("memb.txt").splitlines()
    if str(from_id) not in memb:
        with open("memb.txt", "a", encoding='utf-8') as f: f.write(f"{from_id}\n")
    
    # فحص الحظر
    block = read_file("blocklist.txt").splitlines()
    if str(from_id) in block:
        bot.send_message(chat_id, "⛳| عزي انت محظور من البوت")
        return
    
    h = load("hamsa.json")

    # اذا ضغط على زر الهمسة
    if text == "/start hamsa":
        if str(from_id) in h and h[str(from_id)].get('state') == 'waiting':
            bot.send_message(chat_id, "*⤾حسناً ارسل الهمسة الآن 🧸♥️*")
            h[str(from_id)]['state'] = 'send'
            save("hamsa.json", h)
        return
    
    # ستارت العادي
    sta = read_file("start.txt") or f"اهلا بك [{name}](tg://user?id={from_id})\n📮 بوت الهمسات السريه"
    bot.send_message(chat_id, sta)

# ====== لوحة الادمن ======
@bot.message_handler(commands=['admin'])
def admin(message):
    if message.from_user.id != ADMIN: return
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("احصائيات الاعضاء🕳", callback_data="mem"))
    markup.add(telebot.types.InlineKeyboardButton("الاذاعه💌", callback_data="bcc"))
    markup.add(telebot.types.InlineKeyboardButton("حذف كل الاحصائيات🃏", callback_data="delbot"))
    bot.send_message(message.chat.id, f"اهلا بك مطوري {filterName(message.from_user.first_name)}", reply_markup=markup)

# ====== نظام الهمسة بالرد ======
@bot.message_handler(func=lambda m: m.text in ["همسه", "همسة", "اهمس", "أهمس"])
def hamsa_reply(message):
    if message.chat.type == "private": return
    if not message.reply_to_message: 
        bot.reply_to(message, "❌ رد على رسالة الشخص الي تريد تدزله همسة")
        return
    if message.reply_to_message.from_user.is_bot: 
        bot.reply_to(message, "لا يمكنك عمل همسة لبوت 🙄")
        return
    if message.reply_to_message.from_user.id == message.from_user.id:
        bot.reply_to(message, "لا يمكنك عمل همسة لنفسك 🙄")
        return
    
    from_id = message.from_user.id
    to_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id
    
    h = load("hamsa.json")
    h[str(from_id)] = {
        'chat_id': chat_id,
        'to': to_id,
        'msg_id': message.message_id,
        'reply_msg_id': message.reply_to_message.message_id,
        'state': 'waiting'
    }
    save("hamsa.json", h)
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("قم بارسال الهمسه بـ الخاص🧸♥️", callback_data=f"hamsa|{from_id}"))
    bot.reply_to(message, "*اهلا بك يمكنك الضغط على الزر وإرسال الهمسة في ⤾خاص البوت 🧸♥️*", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("hamsa|"))
def hamsa_private(call):
    bot.answer_callback_query(call.id, url=f"https://t.me/{UserBot}?start=hamsa")

@bot.message_handler(func=lambda m: str(m.from_user.id) in load("hamsa.json") and load("hamsa.json")[str(m.from_user.id)].get('state') == 'send')
def get_hamsa_text(message):
    from_id = message.from_user.id
    text = message.text
    h = load("hamsa.json")
    data = h[str(from_id)]
    
    bot.send_message(message.chat.id, "*⤾ . تم ارسال الهمسة بنجاح 🥳✅*")
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("فتـح الهمسـه 🧧", callback_data=f"{data['to']}&{from_id}"),
        telebot.types.InlineKeyboardButton("حذف الهمسة 🚫", callback_data=f"del#{from_id}")
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
@bot.callback_query_handler(func=lambda call: "&" in call.data)
def open_hamsa(call):
    to_id, from_id = map(int, call.data.split("&"))
    from_id2 = call.from_user.id
    
    h = load("hamsa.json")
    text = h.get(f"msg_{call.message_id}")
    
    if not text: 
        bot.answer_callback_query(call.id, "❌ الهمسة منتهية", show_alert=True)
        return
    
    if from_id2 == to_id or from_id2 == from_id:
        bot.answer_callback_query(call.id, text, show_alert=True)
    else:
        bot.answer_callback_query(call.id, "الهمسة ليست لك", show_alert=True)
        bot.send_message(from_id, f"*لقد حاول هذا المطي كشف همستك 🧑‍🦯🦓*\n\n*المطي :* [{filterName(call.from_user.first_name)}](tg://user?id={from_id2})")

# ====== حذف الهمسة ======
@bot.callback_query_handler(func=lambda call: call.data.startswith("del#"))
def del_hamsa(call):
    from_id = int(call.data.split("#")[1])
    if call.from_user.id == from_id:
        bot.delete_message(call.message.chat.id, call.message_id)
    else:
        bot.answer_callback_query(call.id, "لحذف الهمسة يجب أن تكون انت من ارسل هذه الهمسة", show_alert=True)

# ====== اذاعة ======
@bot.callback_query_handler(func=lambda call: call.data == "bcc" and call.from_user.id == ADMIN)
def bcc_menu(call):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("- اذاعه رساله . 🖤", callback_data="bc"))
    markup.add(telebot.types.InlineKeyboardButton("- الرجوع . 🖤", callback_data="bk"))
    bot.edit_message_text("- اختر نوع الاذاعه المطلوبه . 🖤", call.message.chat.id, call.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "bc" and call.from_user.id == ADMIN)
def bc(call):
    msg = bot.edit_message_text("- ارسل رسالتك الان", call.message.chat.id, call.message_id)
    bot.register_next_step_handler(msg, do_broadcast)

def do_broadcast(message):
    memb = read_file("memb.txt").splitlines()
    c = 0
    for user in memb:
        try: 
            bot.send_message(user, message.text)
            c += 1
            time.sleep(0.1)
        except: pass
    bot.send_message(message.chat.id, f"- تمت الاذاعه لـ {c} عضو . 🖤")

# ====== احصائيات ======
@bot.callback_query_handler(func=lambda call: call.data == "mem" and call.from_user.id == ADMIN)
def mem(call):
    memb = read_file("memb.txt").splitlines()
    band = read_file("blocklist.txt").splitlines()
    bot.edit_message_text(f"*📟┊ احصـائيات البـوت :\n⎚⦁┉⦇  {len(memb)}  ⦈┉⦁⎚ - المشتركيـن\n⎚⦁┉⦇  {len(band)}  ⦈┉⦁⎚ - المحظورين*", call.message.chat.id, call.message_id)

# ====== تشغيل Flask + Bot ======
app = Flask('')
@app.route('/')
def home(): return "Bot is running!"

def run(): app.run(host='0.0.0.0', port=8080)
Thread(target=run).start()

print("Bot Started...")
bot.infinity_polling()
