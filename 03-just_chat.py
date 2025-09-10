import logging
import os
from collections import deque
from http.client import responses

from dotenv import load_dotenv
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler, CallbackContext

#1. Setting up the environment

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')


#Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


# Store user states and chat histories
user_states = {}
chat_histories = {}


SYSTEM_PROMPT = """You are a helpful assistant for a LinkedIn client acquisition service.
Your goal - do it yourself"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to LinkedIn! Say 'magic' to receive a special sign")


def get_giveaway_message(name):
    return f"Hey {name}, Here-s your giveaway"


def has_received_giveaway(user_id, name):
    for message in chat_histories.get(user_id, []):
        if message["role"] == "assistant" and get_giveaway_message(name).lower() in message["content"].lower():
            return True
    return False


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message_text = update.message.text.lower()

    if user_id not in chat_histories:
        chat_histories[user_id] = []

    if message_text == "magic":
        user_states[user_id] = "post_giveaway"

        if has_received_giveaway(user_id, update.message.from_user.first_name):
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You are already received the giveaway! I will send it again")
            await context.bot.send_message(chat_id=update.effective_chat.id, text=get_giveaway_message(update.message.from_user.first_name))
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=get_giveaway_message(update.message.from_user.first_name))
        initial_question = "Congratulations on receiving the giveaway! I am curious, what's your experience been like with finding clients on LinkedIn"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=initial_question)
        chat_histories[user_id].append({"role": "assistant", "content": initial_question})

    elif user_id in user_states:
        chat_histories[user_id].append({"role": "user", "content": message_text})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                      *chat_histories[user_id]
                      ]
        )

        ai_message = response.choices[0].message.content
        chat_histories[user_id].append({"role": "assistant", "content": ai_message})

        await context.bot.send_message(chat_id=update.effective_chat.id, text=ai_message)

        if "book" in ai_message.lower() or "schedule" in ai_message.lower():
            user_states[user_id] = "booking"
            await context.bot.send_message(chat_id=update.effective_chat.id, text="It sounds like you might benefit from a more in-depth conversation"
                                           )

    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to LinkedIn! Say 'magic' to receive a special sign")

application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

start_handler = CommandHandler('start', start)
message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)

application.add_handler(start_handler)
application.add_handler(message_handler)

application.run_polling()