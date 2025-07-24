import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

USER_DATA_DIR = "data_users"
os.makedirs(USER_DATA_DIR, exist_ok=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_file = os.path.join(USER_DATA_DIR, f"{user_id}.txt")

    # Load previous conversation or start fresh
    if os.path.exists(user_file):
        with open(user_file, "r", encoding="utf-8") as f:
            previous_text = f.read()
    else:
        previous_text = ""

    # Append new message
    new_user_text = update.message.text.strip()
    if previous_text:
        # Join previous with new separated by newline for clarity
        combined_text = previous_text + "\nUser: " + new_user_text
    else:
        combined_text = "User: " + new_user_text

    # Save combined text back to file for future use
    with open(user_file, "w", encoding="utf-8") as f:
        f.write(combined_text)

    # Prepare URL encode text param (safe)
    import urllib.parse
    encoded_text = urllib.parse.quote(combined_text)

    api_url = f"https://apis.davidcyriltech.my.id/ai/gpt4?text={encoded_text}"

    try:
        response = requests.get(api_url)
        data = response.json()

        if data.get("success"):
            reply_message = data.get("message", "No message received from AI.")
            # Append AI response to conversation file as well
            updated_text = combined_text + "\nAI: " + reply_message
            with open(user_file, "w", encoding="utf-8") as f:
                f.write(updated_text)
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