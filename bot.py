import telebot
import os
from flask import Flask
from threading import Thread

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

ADMIN_ID = 1076477010 # حط ايديك ادمن

# ====== ملفات الحماية ======
os.makedirs("protect", exist_ok=True)

def read_group(gid, file):
    f = f"protect/{gid}_{file}.txt"
    return "on" if os.path.exists(f) and open(f).read().strip()=="on" else "off"

def write_group(gid, file, status):
    f = f"protect/{gid}_{file}.txt"
    with open(f, 'w') as file: file.write(status)

# ====== كلمات ممنوعة ======
BANNED_WORDS = ["t.me/", "http://", "https://", ".com", "تيليجرام", "رابط"]

# ====== اوامر الادمن ======
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"🔰 اهلا انا بوت الحماية\nضفني للمجموعة وارفعني ادمن بكل الصلاحيات")

@bot.message_handler(commands=['admin'])
def admin(message):
    if message.from_user.id!= ADMIN_ID: return
    gid = message.chat.id
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(f"الروابط: {read_group(gid,'link')}", callback_data="link"))
    markup.add(telebot.types.InlineKeyboardButton(f"الاعضاء بدون اسم: {read_group(gid,'name')}", callback_data="name"))
    markup.add(telebot.types.InlineKeyboardButton(f"منع التكرار: {read_group(gid,'spam')}", callback_data="spam"))
    bot.send_message(message.chat.id, "⚙️ لوحة تحكم الحماية", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    gid = call.message.chat.id
    if call.data == "link":
        new = "off" if read_group(gid,'link')=="on" else "on"
        write_group(gid,'link',new)
        bot.edit_message_text(f"تم: منع الروابط {new}", call.message.chat.id, call.message_id)
    if call.data == "name":
        new = "off" if read_group(gid,'name')=="on" else "on"
        write_group(gid,'name',new)
        bot.edit_message_text(f"تم: طرد بدون اسم {new}", call.message.chat.id, call.message_id)
    if call.data == "spam":
        new = "off" if read_group(gid,'spam')=="on" else "on"
        write_group(gid,'spam',new)
        bot.edit_message_text(f"تم: منع التكرار {new}", call.message.chat.id, call.message_id)

# ====== نظام الحماية ======
user_msg_count = {}

@bot.message_handler(content_types=['text','photo','video','document','sticker'])
def protect(message):
    gid = message.chat.id
    uid = message.from_user.id
    text = message.text or message.caption or ""

    # تخطي الادمن
    try:
        if bot.get_chat_member(gid, uid).status in ['administrator','creator']:
            return
    except: pass

    # 1. منع الروابط
    if read_group(gid,'link') == "on":
        for word in BANNED_WORDS:
            if word in text.lower():
                bot.delete_message(gid, message.message_id)
                bot.send_message(gid, f"🚫 [{message.from_user.first_name}](tg://user?id={uid}) ممنوع نشر الروابط", parse_mode="Markdown")
                return

    # 2. طرد الاعضاء بدون اسم
    if read_group(gid,'name') == "on":
        if not message.from_user.first_name or message.from_user.first_name == "":
            bot.kick_chat_member(gid, uid)
            bot.send_message(gid, f"🚷 تم طرد عضو بدون اسم")
            return

    # 3. منع التكرار / التفليش
    if read_group(gid,'spam') == "on":
        if uid not in user_msg_count: user_msg_count[uid] = 0
        user_msg_count[uid] += 1
        if user_msg_count[uid] > 5: # اكثر من 5 رسائل
            bot.kick_chat_member(gid, uid)
            bot.send_message(gid, f"🚫 تم طرد [{message.from_user.first_name}](tg://user?id={uid}) بسبب التفليش", parse_mode="Markdown")
            user_msg_count[uid] = 0

# 4. حماية الدخول
@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    for new in message.new_chat_members:
        if read_group(message.chat.id,'name') == "on":
            if not new.first_name:
                bot.kick_chat_member(message.chat.id, new.id)
                bot.send_message(message.chat.id, f"🚷 تم طرد {new.id} دخل بدون اسم")
            else:
                bot.send_message(message.chat.id, f"👋 اهلا {new.first_name} نورت الكروب")

# ====== تشغيل ======
app = Flask('')
@app.route('/')
def home(): return "Protection Bot is running!"

def run(): app.run(host='0.0.0.0', port=8080)
Thread(target=run).start()

print("Protection Bot Started...")
bot.infinity_polling()
