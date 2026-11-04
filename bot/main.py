# --- work with paths ---
from dotenv import load_dotenv
from pathlib import Path
import sys
import os




# --- adds the project folder to the top of the list of places where Python searches for modules to import ---
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video_note_bot.settings')



import asyncio
from aiogram import Bot, Dispatcher
import django

django.setup()


# --- getting BASE_DIR and load .env ---
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')





# --- import all handlers ---
from bot.handlers import register_all_handlers
from logger import logger




# --- get a token from .env ---
token = (os.getenv('TOKEN') or '').strip()
if not token:
    logger.error('no TOKEN in .env')


    raise SystemExit(
        "Fill in the TOKEN in the file .env\n\n"
        "Example:\n"
        "TOKEN=123456789:AAExampleTokenFromBotFather"
    )






async def main():
    bot = Bot(token=token)
    dp = Dispatcher()


    logger.info('bot started')

    # --- register all handlers
    register_all_handlers(dp)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())