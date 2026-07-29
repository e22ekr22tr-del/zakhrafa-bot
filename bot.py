import telebot
import os
from flask import Flask
from threading import Thread
import random

BOT_TOKEN = os.environ.get("BOT_TOKEN")
DEVELOPER = "@E22EE"
CHANNEL = "SSLGS" # <-- غيره لمعرف قناتك بدون @
ADMIN_ID = 1076477010 # ايدك

bot = telebot.TeleBot(BOT_TOKEN)

# ===== ملفات التخزين =====
def get_members():
    if not os.path.exists("memb.txt"): return []
    return [x.strip() for x in open("memb.txt").read().splitlines() if x.strip()]

def add_member(user_id):
    members = get_members()
    if str(user_id) not in members:
        with open("memb.txt", "a") as f: f.write(f"{user_id}\n")

def get_block():
    if not os.path.exists("blocklist.txt"): return []
    return [x.strip() for x in open("blocklist.txt").read().splitlines() if x.strip()]

def add_block(user_id):
    with open("blocklist.txt", "a") as f: f.write(f"{user_id}\n")

def remove_block(user_id):
    members = get_block()
    if str(user_id) in members:
        members.remove(str(user_id))
        with open("blocklist.txt", "w") as f: f.write("\n".join(members))

def check_subscription(user_id):
    try:
        status = bot.get_chat_member(chat_id=f"@{CHANNEL}", user_id=user_id)
        return status.status in ['member', 'administrator', 'creator']
    except:
        return False

# ===== الزخرفة =====
def send_zakhrafa(chat_id, text):
    items = ['♡', '◈', '✧', '★', '〲', '『』', '۝', '々', '╰‿╯', '꧁꧂', '𓃠', '⚚']
    smile = random.choice(items)
    
    zakhraf = [
        f"{smile} {text} {smile}",
        f"◈ {text} ◈",
        f"✧･ﾟ: *{text}* :ﾟ･✧",
        f"★彡 {text} 彡★",
        f"『{text}』",
        f"꧁༒☬{text}☬༒꧂",
        f"々 {text} 々",
        f"۝ {text} ۝",
        f"╰‿╯ {text} ╰‿╯",
        f"♡ {text} ♡"
    ]
    
    msg = f"🔥 **الزخارف الجاهزة الك** 🔥\n\n" + "\n".join(zakhraf) + f"\n\n━━━━━━━━━━━━\nالمطور: {DEVELOPER}"
    bot.send_message(chat_id, msg, parse_mode="Markdown")

# ===== الاوامر =====
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    add_member(user_id)
    
    if str(user_id) in get_block():
        bot.reply_to(message, "⛳| عزي انت محظور من البوت")
        return
    
    # اشتراك اجباري
    if not check_subscription(user_id):
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(text="🔔 اشترك بالقناة", url=f"https://t.me/{CHANNEL}"))
        bot.send_message(message.chat.id, f"""⚠️ **تنبيه مهم**
لاستخدام البوت عليك الاشتراك اولا في قناة المطور

بعد الاشتراك اضغط /start

━━━━━━━━━━━━
المطور: {DEVELOPER}""", reply_markup=keyboard, parse_mode="Markdown")
        return
    
    msg = f"""🤍 **اهلا بك {name}**
في بوت الزخرفة التلقائي ☪

ارسل اي اسم او كلمة وسأزخرفها لك فوراً 🔥

━━━━━━━━━━━━
المطور: {DEVELOPER}
"""
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def zakhrafa(message):
    user_id = message.from_user.id
    text = message.text
    
    if str(user_id) in get_block(): return
    if text.startswith('/'): return
    
    # اشتراك اجباري
    if not check_subscription(user_id):
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(text="🔔 اشترك بالقناة", url=f"https://t.me/{CHANNEL}"))
        bot.send_message(message.chat.id, "⚠️ لازم تشترك بالقناة اولاً", reply_markup=keyboard)
        return
    
    send_zakhrafa(message.chat.id, text)

# ===== اوامر الادمن =====
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID: return
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton("احصائيات", callback_data="stats"),
        telebot.types.InlineKeyboardButton("حظر", callback_data="ban")
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton("الغاء حظر", callback_data="unban"),
        telebot.types.InlineKeyboardButton("اذاعة", callback_data="broadcast")
    )
    bot.send_message(message.chat.id, f"**لوحة تحكم المطور**\nالمطور: {DEVELOPER}", reply_markup=keyboard, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.from_user.id != ADMIN_ID: return
    
    if call.data == "stats":
        members = len(get_members())
        blocked = len(get_block())
        bot.edit_message_text(f"💌 عدد الاعضاء: {members}\n💟 المحظورين: {blocked}\n\nالمطور: {DEVELOPER}", call.message.chat.id, call.message.message_id)
    
    if call.data == "ban":
        msg = bot.send_message(call.message.chat.id, "ارسل ايدي العضو للحظر")
        bot.register_next_step_handler(msg, ban_user)
    
    if call.data == "unban":
        msg = bot.send_message(call.message.chat.id, "ارسل ايدي العضو لالغاء الحظر")
        bot.register_next_step_handler(msg, unban_user)
    
    if call.data == "broadcast":
        msg = bot.send_message(call.message.chat.id, "ارسل الرسالة للاذاعة")
        bot.register_next_step_handler(msg, broadcast_msg)

def ban_user(message):
    add_block(message.text)
    bot.reply_to(message, f"تم حظر العضو: {message.text}")

def unban_user(message):
    remove_block(message.text)
    bot.reply_to(message, f"تم الغاء حظر العضو: {message.text}")

def broadcast_msg(message):
    members = get_members()
    for m in members:
        try:
            bot.send_message(m, f"{message.text}\n\n━━━━━━━━━━━━\nالمطور: {DEVELOPER}")
            time.sleep(0.1)
        except: pass
    bot.reply_to(message, f"تمت الاذاعة لـ {len(members)} عضو")

# ===== تشغيل البوت =====
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
print("Bot Started...")
bot.polling(none_stop=True)
