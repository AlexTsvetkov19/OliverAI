import os

from dotenv import load_dotenv
from openai import OpenAI
from pydub import AudioSegment
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, Application

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


async def transcribe_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = await context.bot.get_file(update.message.voice.file_id)
    voice_file = await voice.download_to_drive()

    audio = AudioSegment.from_ogg(voice_file)
    wav_filename = "voice_message.wav"
    audio.export(wav_filename, format="wav")

    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=voice_file
    )
    text = transcription.text

    os.remove(voice_file)
    os.remove(wav_filename)

    return text


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text:
        message_text = update.message.text.lower()
    elif update.message.voice:
        message_text = await transcribe_voice_message(update, context)
        print(message_text)
    else:
        await context.bot.send_message(chat_id=update.message.chat_id, text="Sorry, I can only process text and voice messages.")
        return

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

message_handler = MessageHandler(filters.TEXT | filters.VOICE, handle_message)
app.add_handler(message_handler)
app.run_polling()