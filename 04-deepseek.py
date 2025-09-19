import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.methods import DeleteWebhook
from aiogram.types import Message
import requests
import os
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
IOINTELLIGENCE_API_KEY = os.getenv('IOINTELLIGENCE_API_KEY')


logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN)
dp = Dispatcher()

#Command Start
@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer('Привет! Я бот с подключенной нейросетью, отправь свой запрос', parse_mode='HTML')


#Обработчик любого сообщения
@dp.message()
async def filter_messages(message: Message):
    url = "https://api.intelligence.io.solutions/api/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {IOINTELLIGENCE_API_KEY}"
    }

    data = {
        "model": "deepseek-ai/DeepSeek-R1-0528",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": message.text
            }
        ]
    }


    response = requests.post(url, headers=headers, json=data)
    data2 = response.json()
    pprint(data2)
    text = data2['choices'][0]['message']['content']
    bot_text = text.split('</think>\n')[1]
    print(len(text))

    await message.answer(bot_text, parse_mode='HTML')  # Markdown


async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())