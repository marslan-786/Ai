# یہ آپ کی bot.py فائل ہے (backup system کے ساتھ)

import os
import json
import requests
import zipfile
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")  # یا یہاں لکھ دیں
API_URL = "https://apis.davidcyriltech.my.id/ai/gpt4"
USER_DATA_FOLDER = "data"
OWNER_ID = 8003357608  # ← یہاں اپنا Telegram ID لگائیں

os.makedirs(USER_DATA_FOLDER, exist_ok=True)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Welcome! I'm your GPT-4 bot. Type anything to start chatting.")

# /reset command
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_file = os.path.join(USER_DATA_FOLDER, f"{user_id}.json")
    if os.path.exists(user_file):
        os.remove(user_file)
        await update.message.reply_text("✅ Chat history reset.")
    else:
        await update.message.reply_text("📭 No history found.")

# 🆕 /backup command (owner only)
async def backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ You are not authorized to use this command.")
        return

    zip_path = "user_backup.zip"

    # Create zip file
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for filename in os.listdir(USER_DATA_FOLDER):
            filepath = os.path.join(USER_DATA_FOLDER, filename)
            zipf.write(filepath, arcname=filename)

    # Send zip file to owner
    await update.message.reply_document(document=open(zip_path, "rb"), filename="user_backup.zip")

    # Optional: Delete zip file afterwards
    os.remove(zip_path)

# Main message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    text = update.message.text.strip()
    user_file = os.path.join(USER_DATA_FOLDER, f"{user_id}.json")

    # Load existing context
    if os.path.exists(user_file):
        with open(user_file, "r") as f:
            messages = json.load(f)
    else:
        messages = []

    # Add user message
    messages.append({"role": "user", "content": text})

    # Send to GPT API
    try:
        response = requests.post(
            API_URL,
            json={"messages": messages},
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        if response.status_code == 200:
            reply = response.json().get("response", "🤖 No reply received.")
            messages.append({"role": "assistant", "content": reply})
            with open(user_file, "w") as f:
                json.dump(messages, f, indent=2)
            await update.message.reply_text(reply)
        else:
            await update.message.reply_text(f"⚠️ API Error: {response.status_code}")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")

# Run the bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("backup", backup))  # 🆕 Backup handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot is running...")
    app.run_polling()