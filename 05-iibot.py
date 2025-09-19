import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.methods import DeleteWebhook
from aiogram.types import Message
import requests
import os
import aiohttp
import json
from dotenv import load_dotenv
from pprint import pprint
from typing import Optional, Dict, Any

load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
IOINTELLIGENCE_API_KEY = os.getenv('IOINTELLIGENCE_API_KEY')

logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN)
dp = Dispatcher()


class APIRequestHandler:
    """Класс для обработки API запросов с проверками"""

    def __init__(self, timeout: int = 120, max_response_length: int = 4096):
        self.timeout = timeout  # 2 минуты в секундах
        self.max_response_length = max_response_length  # Максимальная длина для Telegram

    async def make_api_request(self, url: str, headers: Dict[str, str],
                               data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Выполняет асинхронный API запрос с проверками

        Args:
            url: URL API endpoint
            headers: заголовки запроса
            data: данные запроса

        Returns:
            Ответ API или None в случае ошибки
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        url,
                        headers=headers,
                        json=data,
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:

                    # Проверяем статус код
                    if response.status != 200:
                        logging.error(f"API ошибка: статус код {response.status}")
                        return None

                    # Получаем и проверяем длину ответа
                    response_text = await response.text()

                    if len(response_text) > self.max_response_length * 10:  # Буфер для JSON
                        logging.error(f"Ответ слишком длинный: {len(response_text)} символов")
                        return None

                    if not response_text.strip():
                        logging.error("Пустой ответ от API")
                        return None

                    return await response.json()

        except asyncio.TimeoutError:
            logging.error(f"Превышено время ожидания ({self.timeout} секунд)")
            return None
        except aiohttp.ClientError as e:
            logging.error(f"Ошибка сети: {e}")
            return None
        except json.JSONDecodeError as e:
            logging.error(f"Ошибка парсинга JSON: {e}")
            return None


# Command Start
@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer('Привет! Я бот с подключенной нейросетью, отправь свой запрос', parse_mode='HTML')


# Обработчик любого сообщения
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

    # Создаем обработчик запросов
    api_handler = APIRequestHandler(timeout=120, max_response_length=4096)

    # Выполняем запрос
    response_data = await api_handler.make_api_request(url, headers, data)

    if response_data is None:
        await message.answer("⚠️ Произошла ошибка при обработке запроса. Попробуйте позже.")
        return

    try:
        # Обрабатываем ответ
        text = response_data['choices'][0]['message']['content']

        # Разделяем текст (если есть теги)
        if '</think>\n' in text:
            bot_text = text.split('</think>\n')[1]
        else:
            bot_text = text

        # Проверяем длину текста для Telegram (максимум 4096 символов)
        if len(bot_text) > 4096:
            logging.warning(f"Текст слишком длинный для Telegram: {len(bot_text)} символов")
            # Обрезаем текст или разбиваем на части
            bot_text = bot_text[:4000] + "...\n\n⚠️ Сообщение было обрезано из-за ограничений Telegram"

        await message.answer(bot_text, parse_mode='HTML')

    except KeyError as e:
        logging.error(f"Ошибка в структуре ответа API: {e}")
        pprint(response_data)  # Для отладки
        await message.answer("❌ Ошибка в формате ответа от нейросети")
    except Exception as e:
        logging.error(f"Неожиданная ошибка: {e}")
        await message.answer("⚠️ Произошла непредвиденная ошибка")


async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())