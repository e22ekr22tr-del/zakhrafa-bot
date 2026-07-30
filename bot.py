import json
import os
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# ================== الاعدادات ==================
TOKEN = os.getenv("TOKEN")
ADMIN_ID = 1076477010
USER_BOT = "Tik_TokLBOT"
CHANNEL = "SSLGS"
DEV = "E22EE"
# =================================================

HAMSAS_FILE = "hamsas.json"
USERS_FILE = "users.json"

def load_json(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(data, file):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_footer_buttons():
    return [
        [InlineKeyboardButton("👨‍💻 المطور", url=f"https://t.me/{DEV}"),
         InlineKeyboardButton("📢 القناة", url=f"https://t.me/{CHANNEL}")]
    ]

def escape_md(text):
    # نهرب الرموز حتى ما يوكع البوت
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', str(text))

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not CHANNEL: return True
    try:
        member = await context.bot.get_chat_member(chat_id=f"@{CHANNEL}", user_id=update.effective_user.id)
        if member.status in ["member", "administrator", "creator"]:
            return True
    except:
        pass
    keyboard = [[InlineKeyboardButton("🔔 اشترك بالقناة", url=f"https://t.me/{CHANNEL}")]]
    text = "⚠️ عذراً يجب الاشتراك في القناة اولا لاستخدام البوت"
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif update.callback_query:
        await update.callback_query.answer("اشترك بالقناة اولا", show_alert=True)
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_join(update, context): return
    hamsas = load_json(HAMSAS_FILE) # نعيد التحميل كل مرة
    if context.args and context.args[0].startswith("whisper_"):
        msg_id = context.args[0]
        if msg_id in hamsas:
            hamsas[msg_id]["waiting"] = True
            save_json(hamsas, HAMSAS_FILE)
            return await update.message.reply_text("تمام ارسل الهمسة هسه ✍️", reply_markup=InlineKeyboardMarkup(get_footer_buttons()))
    keyboard = get_footer_buttons()
    await update.message.reply_text("اهلا بيك ببوت الهمسات 🧸♥️\n\nبالكروب رد واكتب همسه", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_join(update, context): return
    if update.message.chat.type == "private": return
    if not update.message.reply_to_message: return
    if "همسه" not in update.message.text and "همسة" not in update.message.text: return

    hamsas = load_json(HAMSAS_FILE)
    sender = update.message.from_user.id
    target = update.message.reply_to_message.from_user.id
    chat_id = update.message.chat.id
    msg_id = f"whisper_{chat_id}_{update.message_id}_{int(time.time())}" # ضفنا الوقت حتى ما يتكرر

    if sender == target: return await update.message.reply_text("متكدر تهمس لنفسك 🙄")
    if update.message.reply_to_message.from_user.is_bot: return await update.message.reply_text("متكدر تهمس لبوت 🙄")

    hamsas[msg_id] = {"sender": sender, "target": target, "chat_id": chat_id, "text": "", "waiting": False, "message_id": 0, "reply_id": update.message_id}
    save_json(hamsas, HAMSAS_FILE)

    keyboard = [
        [InlineKeyboardButton("ارسال الهمسة بالخاص", url=f"https://t.me/{USER_BOT}?start={msg_id}")],
        *get_footer_buttons()
    ]
    await update.message.reply_text("دوس الزر وارسل الهمسة بالخاص", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_private_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_join(update, context): return
    hamsas = load_json(HAMSAS_FILE)
    users = load_json(USERS_FILE)
    user = update.effective_user
    user_id = user.id

    found_msg_id = None
    for msg_id, data in hamsas.items():
        if data.get("sender") == user_id and data.get("waiting") == True:
            found_msg_id = msg_id
            break
    
    if not found_msg_id:
        return await update.message.reply_text("ماكو همسة منتظرة. ارجع للكروب ودوس الزر اول")

    hamsas[found_msg_id]["text"] = update.message.text
    hamsas[found_msg_id]["waiting"] = False
    save_json(hamsas, HAMSAS_FILE)

    if str(user_id) not in users:
        users[str(user_id)] = {"count": 0}
    users[str(user_id)]["count"] += 1
    count = users[str(user_id)]["count"]
    save_json(users, USERS_FILE)

    caption = f"💌 لديك همسة جديدة\n**عدد الهمسات:** {count}"

    keyboard = [
        [InlineKeyboardButton("📩 فتح الهمسة", callback_data=f"open_{found_msg_id}"),
         InlineKeyboardButton("🗑️ حذف", callback_data=f"del_{found_msg_id}")],
        *get_footer_buttons()
    ]

    data = hamsas[found_msg_id]
    try:
        sent_msg = await context.bot.send_message(
            chat_id=data["chat_id"],
            text=caption,
            reply_to_message_id=data["reply_id"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        print("Send Error:", e)
        return

    hamsas[found_msg_id]["message_id"] = sent_msg.message_id
    save_json(hamsas, HAMSAS_FILE)
    await update.message.reply_text("تم ارسال الهمسة ✅", reply_markup=InlineKeyboardMarkup(get_footer_buttons()))

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_join(update, context): return
    hamsas = load_json(HAMSAS_FILE)
    query = update.callback_query
    await query.answer()
    data = query.data
    msg_id = data.split("_", 1)[1]

    if msg_id not in hamsas:
        return await query.answer("الهمسة انحذفت", show_alert=True)

    hamsa = hamsas[msg_id]

    if data.startswith("open_"):
        if query.from_user.id == hamsa["target"] or query.from_user.id == hamsa["sender"]:
            text = hamsa["text"]
            if not text:
                return await query.answer("المرسل لسه ما كتب الهمسة", show_alert=True)
            await query.answer(f"📩 {text}", show_alert=True)
        else:
            await query.answer("الهمسة ليست لك 🧑‍🦯", show_alert=True)

    elif data.startswith("del_"):
        if query.from_user.id == hamsa["sender"]:
            await query.answer("تم حذف الهمسة")
            try: await context.bot.delete_message(chat_id=hamsa["chat_id"], message_id=hamsa["message_id"])
            except: pass
            del hamsas[msg_id]
            save_json(hamsas, HAMSAS_FILE)
        else:
            await query.answer("بس المرسل يكدر يحذفها", show_alert=True)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_group))
app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & ~filters.COMMAND, handle_private_text))
app.add_handler(CallbackQueryHandler(buttons))

print("البوت شغال...")
app.run_polling()
