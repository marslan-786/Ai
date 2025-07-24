import os
import json
import logging
import requests
from urllib.parse import quote
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# --- Configuration ---
BOT_TOKEN = os.getenv("BOT_TOKEN") or "your_bot_token_here"
USER_FOLDER = "users"

# --- Create folder if it doesn't exist ---
os.makedirs(USER_FOLDER, exist_ok=True)

# --- Logging setup ---
logging.basicConfig(level=logging.INFO)

# --- Function to save user data ---
def save_user_data(user_id, message):
    filepath = os.path.join(USER_FOLDER, f"{user_id}.json")
    data = {"chat": message}
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- API response function ---
def fetch_api_reply(message: str) -> str:
    try:
        encoded_msg = quote(message)
        url = f"https://apis.davidcyriltech.my.id/ai/chatbot?query={encoded_msg}"
        response = requests.get(url, timeout=10)
        data = response.json()

        if data.get("success"):
            return data.get("message", "✅ API succeeded but no message returned.")
        else:
            return "❌ API did not return a valid response."
    except Exception as e:
        logging.error(f"API error: {e}")
        return "⚠️ Failed to get response from the API."

# --- Handle private chat messages ---
async def handle_private(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text.strip()

    # Save user data
    save_user_data(user_id, message)

    # Call API and send response
    reply = fetch_api_reply(message)
    await update.message.reply_text(reply)

# --- Handle /ask in group chats only (no data saving) ---
async def handle_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        message = " ".join(context.args)
        reply = fetch_api_reply(message)
        await update.message.reply_text(reply)
    else:
        await update.message.reply_text("❌ Please use it like `/ask your question`.")

# --- /start command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n\nSend any message in private chat, or use `/ask your question` in a group."
    )

# --- Main bot application ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ask", handle_ask))  # For group chats

    # Only handle and save data for private text messages
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT, handle_private))

    print("✅ Bot is running...")
    app.run_polling()
    