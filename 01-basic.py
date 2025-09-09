import os
from http.client import responses

from dotenv import load_dotenv

from telegram import Update
from telegram.ext import ApplicationBuilder,CommandHandler, MessageHandler, filters, ContextTypes


load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    response = ""
    if "start" in user_message.lower():
        response = "Welcome to OliverAI!"
    elif "what's up" in user_message.lower():
        response = "I'm here to help with LindedIn client acquisition. Say 'magic' to receive a special giveaway!"

    if response:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    return

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", handle_message))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()