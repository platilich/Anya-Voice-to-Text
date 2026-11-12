# --- work with paths ---
from pathlib import Path
import os
import sys
from dotenv import load_dotenv



# --- adds the project folder to the top of the list of places where Python searches for modules to import ---
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

load_dotenv(BASE_DIR / ".env")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "video_note_bot.settings")


import asyncio
import django
django.setup()

from aiogram import Bot, Dispatcher
from aiogram.types import FSInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from users.models import TelegramUser
from bot.handlers import register_all_handlers
from bot.logger import logger
from broadcast_manage.models import BroadcastTime, BroadcastStatus, BroadcastTexts





# --- get a token from .env ---
token = (os.getenv('TOKEN') or '').strip()
if not token:
    logger.error('no TOKEN in .env')


    raise SystemExit(
        "Fill in the TOKEN in the file .env\n\n"
        "Example:\n"
        "TOKEN=123456789:AAExampleTokenFromBotFather"
    )




async def broadcast_limits_updated(bot):
    if await BroadcastStatus.broadcast_not_work():
        return


    users_id = await TelegramUser.get_all_users()

    time_updated = await BroadcastTexts.get_broadcast_text()


    project_root = Path(__file__).resolve().parent.parent
    screen_file = project_root / "screens" / "free_minutes.jpeg"
    photo = FSInputFile(screen_file)


    for user_id in users_id:
        try:
            await TelegramUser.add_seconds(user_id, seconds=180)

            await bot.send_photo(
                chat_id=user_id,
                photo=photo,
                caption=time_updated,
                parse_mode='HTML'
            )


        except Exception as e:
            logger.error(f'failed to send a mailing list message to the user: {e}')





async def main():
    bot = Bot(token=token)
    dp = Dispatcher()


    logger.info('bot started')


    register_all_handlers(dp)


    scheduler = AsyncIOScheduler(timezone="UTC")


    scheduled_at = await BroadcastTime.get_time_broadcast()


    scheduler.add_job(
        broadcast_limits_updated,
        trigger="cron",
        hour=scheduled_at.hour,
        minute=scheduled_at.minute,
        args=[bot],
        id="daily_minutes",
        replace_existing=True,
    )




    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())