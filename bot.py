# یہ آپ کی bot.py فائل ہے
import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# 🔐 Replace with your actual token
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    api_url = f"https://apis.davidcyriltech.my.id/ai/gpt4?text={user_input}"

    try:
        response = requests.get(api_url)
        data = response.json()

        if data.get("success"):
            reply_message = data.get("message", "No message received from AI.")
        else:
            reply_message = "❌ API error: No valid response."

    except Exception as e:
        logging.error(f"API error: {e}")
        reply_message = "⚠️ Failed to connect to the AI API."

    await update.message.reply_text(reply_message)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()