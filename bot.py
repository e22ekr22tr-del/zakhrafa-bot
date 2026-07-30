import json
import os
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# ================== الاعدادات ==================
TOKEN = os.getenv("TOKEN")
ADMIN_ID = 1076477010
USER_BOT = "Tik_TokLBOT"
# =================================================

HAMSAS_FILE = "hamsas.json"

def load_json(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"pending": {}, "hamsas": {}} # نظامين

def save_json(data, file):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

db = load_json(HAMSAS_FILE)

def filterName(name):
    scam = ['[','*',']','_','(',')','`']
    for s in scam: name = name.replace(s, '')
    return name

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args and context.args[0].startswith("hamsa"):
        user_id = str(update.effective_user.id)
        if user_id in db["pending"]:
            db["pending"][user_id]["state"] = "send"
            save_json(db, HAMSAS_FILE)
            return await update.message.reply_text("تمام ارسل الهمسة هسه ✍️")
        else:
            return await update.message.reply_text("⚠️ لا توجد همسة بانتظارك")
    
    keyboard = [[InlineKeyboardButton("➕ ضفني لمجموعتك", url=f"https://t.me/{USER_BOT}?startgroup=true")]]
    await update.message.reply_text("🌹 **اهلا بيك ببوت الهمسات السريه** 🌹\n\n🧸 رد على رسالة الشخص واكتب `همسة`", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def handle_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == "private": return
    if not update.message.reply_to_message: return
    if update.message.text.strip() not in ["همسه", "همسة", "اهمس", "أهمس"]: return

    sender = update.message.from_user.id
    target = update.message.reply_to_message.from_user.id
    chat_id = update.message.chat.id
    reply_id = update.message.message_id

    if sender == target: return await update.message.reply_text("😒 لا يمكنك عمل همسة لنفسك")
    if update.message.reply_to_message.from_user.is_bot: return await update.message.reply_text("😒 لا يمكنك عمل همسة لبوت")

    hamsa_id = str(int(time.time()))
    user_id = str(sender)

    db["pending"][user_id] = {
        "chat_id": chat_id,
        "to": target,
        "reply_msg_id": reply_id,
        "hamsa_id": hamsa_id,
        "state": "waiting"
    }
    save_json(db, HAMSAS_FILE)

    keyboard = [[InlineKeyboardButton("❤️ ارسل الهمسة بالخاص", url=f"https://t.me/{USER_BOT}?start=hamsa")]]
    await update.message.reply_text("اهلا بك دوس الزر وارسل الهمسة بالخاص 🧸♥️", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_private_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    if user_id not in db["pending"] or db["pending"][user_id].get("state") != "send":
        return await update.message.reply_text("ماكو همسة منتظرة. ارجع للكروب ودوس الزر اول")

    data = db["pending"][user_id]
    text = update.message.text
    hamsa_id = data["hamsa_id"]

    await update.message.reply_text("⤾ . تم ارسال الهمسة بنجاح 🥳✅")

    db["hamsas"][hamsa_id] = {
        "text": text,
        "from": data["to"], # المستلم
        "to": user_id # المرسل - خليته عكس حتى يطابق منطقك
    }
    
    keyboard = [
        [InlineKeyboardButton("🧧 فتح الهمسه", callback_data=f"open_{hamsa_id}"),
         InlineKeyboardButton("🚫 حذف", callback_data=f"del_{hamsa_id}")]
    ]

    await context.bot.send_message(
        chat_id=data["chat_id"],
        text=f"*⤾ . ؏ــمرري 🧸♥️ لديك همسة من*\n[{filterName(update.effective_user.first_name)}](tg://user?id={user_id})",
        reply_to_message_id=data["reply_msg_id"],
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

    del db["pending"][user_id]
    save_json(db, HAMSAS_FILE)

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    hamsa_id = data.split("_")[1]

    if hamsa_id not in db["hamsas"]:
        return await query.answer("❌ الهمسة منتهية او محذوفة", show_alert=True)

    hamsa = db["hamsas"][hamsa_id]
    from_id = int(hamsa["to"]) # المرسل
    to_id = int(hamsa["from"]) # المستلم

    if data.startswith("open_"):
        if query.from_user.id == from_id or query.from_user.id == to_id:
            await query.answer(f"💌 الهمسة:\n\n{hamsa['text']}", show_alert=True)
        else:
            await query.answer("🔒 الهمسة ليست لك", show_alert=True)
            await context.bot.send_message(from_id, f"*⚠️ لقد حاول هذا الشخص كشف همستك*\n\n*الشخص:* [{filterName(query.from_user.first_name)}](tg://user?id={query.from_user.id})", parse_mode="Markdown")

    elif data.startswith("del_"):
        if query.from_user.id == from_id:
            del db["hamsas"][hamsa_id]
            save_json(db, HAMSAS_FILE)
            try: await context.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message_id)
            except: pass
            await query.answer("✅ تم حذف الهمسة")
        else:
            await query.answer("لحذف الهمسة يجب أن تكون انت من ارسل هذه الهمسة", show_alert=True)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_group))
app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_private_text))
app.add_handler(CallbackQueryHandler(buttons))

print("البوت شغال...")
app.run_polling()
