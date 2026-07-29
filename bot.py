import telebot
import os
import random
from flask import Flask
from threading import Thread

BOT_TOKEN = os.environ.get("BOT_TOKEN") # حط التوكن هنا بمتغير البيئة
DEVELOPER = "@E22EE"
ADMIN_ID = 1076477010
CHANNEL1 = "SSLGS" # القناة الاولى للاشتراك الاجباري - غيرها
CHANNEL2 = "" # القناة الثانية - فاضية

bot = telebot.TeleBot(BOT_TOKEN)

# ====== ملفات ======
def read_file(f): return open(f).read().strip() if os.path.exists(f) else ""
def write_file(f, data): open(f, 'w').write(data)
def get_members():
    if not os.path.exists("ARMOF4.txt"): return []
    return [x.strip() for x in open("ARMOF4.txt").read().splitlines() if x.strip()]

def add_member(uid):
    members = get_members()
    if str(uid) not in members:
        with open("ARMOF4.txt", "a") as f: f.write(f"{uid}\n")

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
    
    # فحص الاشتراك
    if not check_sub(user_id):
        ch1 = read_file("ARMOF0.txt") or CHANNEL1
        ch2 = read_file("ARMOF1.txt")
        txt = f"""- ▫️ عذراً عزيزي ، 🔰
▪️ يجب عليك الإشتراك في القناة أولاً ⚜️؛
- اشترك ثم ارسل /start 📛!

@{ch1}
@{ch2}""" if ch2 else f"اشترك بقناة @{ch1} ثم /start"
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton("اشترك", url=f"https://t.me/{ch1}"))
        bot.send_message(message.chat.id, txt, reply_markup=keyboard)
        return

    bot.send_message(message.chat.id, f"[{name}](tg://user?id={user_id})\n📮☑:مرحبا بك\nالمطور: {DEVELOPER}", parse_mode="Markdown", reply_markup=main_menu())

def main_menu():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("زخرفه الاسماء ♡", callback_data='ZARMOF'))
    markup.add(telebot.types.InlineKeyboardButton("بايو قنوات تلي ♡", callback_data='bio'))
    markup.row(
        telebot.types.InlineKeyboardButton("رموز نادره ♡", callback_data='med'),
        telebot.types.InlineKeyboardButton("نبذ جاهزه ♡", callback_data='mem')
    )
    markup.add(telebot.types.InlineKeyboardButton("اسماء جاهزه ♡", callback_data='mido'))
    markup.row(
        telebot.types.InlineKeyboardButton(f"D𝐄𝐕 ♡ {DEVELOPER}", callback_data='dev'),
        telebot.types.InlineKeyboardButton("𓆩 We 𓆪", url='https://t.me/SSLGS')
    )
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    uid = call.from_user.id
    if call.data == "ZARMOF":
        write_file(f"zkref/{uid}/zeakef.txt", "ARMOF0")
        bot.edit_message_text("حـسنـاً ارسـل اسـمكك 😻💞\nW𝒆𝒍 𝒔𝒆𝒏𝒅 𝒚𝒐𝒖𝒓 𝒏𝒂𝒎𝒆", call.message.chat.id, call.message.message_id, reply_markup=back_btn())
    
    elif call.data == "bio":
        write_file(f"LOrDARMOF/{uid}/LOrDdARMOF.txt", "ARMOF0")
        bot.edit_message_text("قـم بـارسـال مـعرفـك فـقط\nO𝒏𝒍𝒚 𝒔𝒆𝒏𝒅 𝒚𝒐𝒖𝒓 𝒂𝒄𝒒𝒖𝒂𝒊𝒏𝒕𝒂𝒏𝒄𝒆", call.message.chat.id, call.message.message_id, reply_markup=back_btn())
    
    elif call.data == "dev":
        bot.edit_message_text(f"『 A𝐑𝐌𝐎𝐅 𝆴𝄵』 𓆩 iraq 🇮🇶 𓆪\n﹎﹎﹎\nالمطور: {DEVELOPER}", call.message.chat.id, call.message.message_id, reply_markup=back_btn())
    
    elif call.data == "back":
        bot.edit_message_text(f"[{call.from_user.first_name}](tg://user?id={uid})\n📮☑:مرحبا بك\n\nالمطور: {DEVELOPER}", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=main_menu())
    
    # لوحة الادمن
    elif call.data == "ARMOF" and uid == ADMIN_ID:
        bot.edit_message_text("لوحة التحكم", call.message.chat.id, call.message.message_id, reply_markup=admin_menu())

def back_btn():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("رجوع", callback_data="back"))
    return markup

def admin_menu():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("وضع قناة 1", callback_data="ARMOF0"))
    markup.add(telebot.types.InlineKeyboardButton("وضع قناة 2", callback_data="ARMOF2"))
    markup.add(telebot.types.InlineKeyboardButton("عدد المشتركين", callback_data="ARMOF7"))
    markup.add(telebot.types.InlineKeyboardButton("رجوع", callback_data="back"))
    return markup

# ====== معالجة الرسائل ======
@bot.message_handler(content_types=['text'])
def handle_text(message):
    uid = message.from_user.id
    text = message.text
    
    if text == "/admin" and uid == ADMIN_ID:
        bot.send_message(message.chat.id, "مرحبا بك في لوحة التحكم", reply_markup=admin_menu())
        return
    
    if text == "/start": return
    
    # زخرفة
    if os.path.exists(f"zkref/{uid}/zeakef.txt") and read_file(f"zkref/{uid}/zeakef.txt") == "ARMOF0":
        for i in range(8):
            bot.send_message(message.chat.id, zakhrafa_text(text))
        write_file(f"zkref/{uid}/zeakef.txt", "")
        return
    
    # بايو
    if os.path.exists(f"LOrDARMOF/{uid}/LOrDdARMOF.txt") and read_file(f"LOrDARMOF/{uid}/LOrDdARMOF.txt") == "ARMOF0":
        bio = f"- T𝗛𝗘 𝗦𝗘𝗖𝗥𝗘𝗧 𝗢𝗙 𝗖𝗛𝗮𝗡𝗚𝗘\n___________\n♡ : ᴹᴬᴺᴳᴱᴿ ➤ {text}\n\nالمطور: {DEVELOPER}"
        bot.send_message(message.chat.id, f"`{bio}`", parse_mode="Markdown")
        write_file(f"LOrDARMOF/{uid}/LOrDdARMOF.txt", "")

# ====== تشغيل ======
app = Flask('')
@app.route('/')
def home(): return "Bot is running!"

def run(): app.run(host='0.0.0.0', port=8080)
Thread(target=run).start()

print("Bot Started...")
bot.polling(none_stop=True)
