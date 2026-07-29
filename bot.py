import telebot
import os
import random
from flask import Flask
from threading import Thread

BOT_TOKEN = os.environ.get("BOT_TOKEN") 
DEVELOPER = "@E22EE"
DEVELOPER_ID = 1076477010  # ايديك للصورة
ADMIN_ID = 1076477010
CHANNEL1 = "SSLGS" 
CHANNEL2 = "" 

bot = telebot.TeleBot(BOT_TOKEN)

# ====== انشاء المجلدات تلقائي ======
os.makedirs("zkref", exist_ok=True)
os.makedirs("2xref/1076477010", exist_ok=True) 

# ====== ملفات ======
def read_file(f): 
    return open(f, encoding='utf-8').read().strip() if os.path.exists(f) else ""

def write_file(f, data): 
    os.makedirs(os.path.dirname(f), exist_ok=True)
    with open(f, 'w', encoding='utf-8') as file:
        file.write(data)

def get_members():
    if not os.path.exists("ARMOF4.txt"): return []
    return [x.strip() for x in open("ARMOF4.txt", encoding='utf-8').read().splitlines() if x.strip()]

def add_member(uid):
    members = get_members()
    if str(uid) not in members:
        with open("ARMOF4.txt", "a", encoding='utf-8') as f: f.write(f"{uid}\n")

def check_sub(user_id):
    ch1 = read_file("ARMOF0.txt")
    ch2 = read_file("ARMOF1.txt")
    try:
        if ch1:
            st = bot.get_chat_member(f"@{ch1}", user_id).status
            if st in ['left', 'kicked']: return False
        if ch2:
            st = bot.get_chat_member(f"@{ch2}", user_id).status
            if st in ['left', 'kicked']: return False
        return True
    except: return False

# ====== الزخرفة ======
def zakhrafa_text(text):
    items = ['♡', '◈', '✧', '★', '〲', '『』', '۝', '々', '╰‿╯', '꧁꧂']
    smile = random.choice(items)
    return f"{text}{smile}"

# ====== الاوامر ======
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    add_member(user_id)
    
    if not check_sub(user_id):
        ch1 = read_file("ARMOF0.txt") or CHANNEL1
        txt = f"اشترك بقناة @{ch1} ثم /start"
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton("🔰 اشترك هنا 🔰", url=f"https://t.me/{ch1}"))
        bot.send_message(message.chat.id, txt, reply_markup=keyboard)
        return

    # رسالة ترحيب فخمة
    welcome = f"""
𓆩 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗭𝗔𝗞𝗛𝗥𝗔𝗙𝗔 𝗕𝗢𝗧 𓆪

مرحباً بك [{name}](tg://user?id={user_id}) 👑
انا بوت زخرفة الاسماء الاحترافي 🔥

✧ يمكنك زخرفة اسمك بـ 8 اشكال مختلفه بضغطة زر
✧ اختار "زخرفه الاسماء" من القائمة ادناه

╭━━━━━━━━━━━━━━╮
   المطور: {DEVELOPER}
╰━━━━━━━━━━━━━━╯
"""
    bot.send_message(message.chat.id, welcome, parse_mode="Markdown", reply_markup=main_menu())

def main_menu():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("♡ زخرفه الاسماء ♡", callback_data='ZARMOF'))
    markup.add(telebot.types.InlineKeyboardButton("📸 صورة المطور", callback_data='dev_photo'))
    markup.add(telebot.types.InlineKeyboardButton("👑 المطور", url=f"https://t.me/{DEVELOPER.replace('@','')}"))
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    uid = call.from_user.id
    if call.data == "ZARMOF":
        write_file(f"zkref/{uid}/zeakef.txt", "ARMOF0")
        bot.edit_message_text("🔮 ارسل اسمك الان وسأزخرفه لك بـ 8 اشكال 🔮", call.message.chat.id, call.message_id, reply_markup=back_btn())
    
    elif call.data == "dev_photo":
        try:
            bot.send_photo(call.message.chat.id, photo=DEVELOPER_ID, caption=f"المطور: {DEVELOPER}\nراسلني اذا احتاجيت شي 👑")
        except:
            bot.send_message(call.message.chat.id, f"المطور: {DEVELOPER}")
    
    elif call.data == "back":
        welcome = f"مرحباً بك [{call.from_user.first_name}](tg://user?id={uid}) 👑\nاختر من القائمة ادناه:"
        bot.edit_message_text(welcome, call.message.chat.id, call.message_id, parse_mode="Markdown", reply_markup=main_menu())

def back_btn():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("⬅️ رجوع", callback_data="back"))
    return markup

@bot.message_handler(content_types=['text'])
def handle_text(message):
    uid = message.from_user.id
    text = message.text
    
    if text == "/start": return
    
    # زخرفة فقط
    if os.path.exists(f"zkref/{uid}/zeakef.txt") and read_file(f"zkref/{uid}/zeakef.txt") == "ARMOF0":
        for i in range(8):
            bot.send_message(message.chat.id, zakhrafa_text(text))
        write_file(f"zkref/{uid}/zeakef.txt", "")
        bot.send_message(message.chat.id, "✅ تمت الزخرفة بنجاح", reply_markup=main_menu())
        return

# ====== تشغيل ======
app = Flask('')
@app.route('/')
def home(): return "Bot is running!"

def run(): app.run(host='0.0.0.0', port=8080)
Thread(target=run).start()

print("Bot Started...")
bot.infinity_polling()
