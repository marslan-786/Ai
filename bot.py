import os
import json
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# --- کنفگریشن ---
BOT_TOKEN = os.getenv("BOT_TOKEN") or "آپ_کا_بوٹ_ٹوکن"
USER_FOLDER = "users"

# --- فولڈر بنائیں اگر موجود نہیں ---
if not os.path.exists(USER_FOLDER):
    os.makedirs(USER_FOLDER)


# --- ڈیٹا محفوظ کرنے کا فنکشن ---
def save_user_data(user_id, message):
    filepath = os.path.join(USER_FOLDER, f"{user_id}.json")
    data = {"chat": message}
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)


# --- AI یا جو بھی API ریسپانس چاہیے ---
async def get_response(message: str) -> str:
    # یہاں اصل API کال لگائیں
    return f"🤖 جواب: {message}"


# --- پرائیویٹ چیٹ میں ہینڈلنگ ---
async def handle_private(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text
    save_user_data(user_id, message)
    reply = await get_response(message)
    await update.message.reply_text(reply)


# --- گروپ چیٹ میں صرف /ask کمانڈ سے بات چیت ---
async def handle_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        message = " ".join(context.args)
        reply = await get_response(message)
        await update.message.reply_text(reply)
    else:
        await update.message.reply_text("❌ برائے مہربانی سوال کے ساتھ استعمال کریں:\n`/ask آپ کا سوال`")


# --- اسٹارٹ کمانڈ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 خوش آمدید! پرائیویٹ چیٹ میں کچھ بھی لکھیں، گروپ میں `/ask سوال` کے ذریعے پوچھیں۔")


# --- مین فنکشن ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ask", handle_ask))  # گروپ چیٹ کمانڈ

    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT, handle_private))# صرف پرائیویٹ چیٹ

    print("✅ Bot is running...")
    app.run_polling()