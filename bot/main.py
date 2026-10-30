import asyncio
import sys
from pathlib import Path
import os
import django

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video_note_bot.settings')
django.setup()



from aiogram import Bot, Dispatcher
from dotenv import load_dotenv


from middlewares.filters import get_rest_time

from bot.handlers import register_all_handlers




BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


token = (os.getenv('TOKEN') or '').strip()
if not token:
    raise SystemExit(
        "Fill in the TOKEN in the file .env\n\n"
        "Example:\n"
        "TOKEN=123456789:AAExampleTokenFromBotFather"
    )



async def main():
    bot = Bot(token=token)
    dp = Dispatcher()




    register_all_handlers(dp)


    await get_rest_time()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())