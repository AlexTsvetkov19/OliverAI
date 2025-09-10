import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.methods import DeleteWebhook
from aiogram.types import Message
import requests
import os

from get_models import response

TOKEN = "8109596230:AAGmKeq9KUwZUpbwWfZJAiuauL3-Jzka9ZE"


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
        "Authorization": "Bearer io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6IjQxN"
                         "2NhNzM0LWEyOGMtNGRiMi04MWEwLWI0OTU5OWJkZWIwMyIsImV4cCI6NDkxMTA3NTMzM"
                         "30.MD-VC1NPfLkiRsG7EH2N-cmXWbzKPev_yrDMu_w5Euo4_5EAY6iLvpE1IgpQPqUWCMyef9UM2l_eB660i6XZfw"
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
    data = response.json()

    text = data['choices'][0]['message']['content']
    bot_text = text.split('</think>\n')[1]

    await message.answer(bot_text, parse_mode='HTML')  # Markdown

async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())