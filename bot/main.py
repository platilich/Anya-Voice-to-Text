import asyncio
import sys
from pathlib import Path
import os
import django



sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video_note_bot.settings')
django.setup()


def ensure_database_ready():
    """Stop early if migrate was not run. Otherwise the first message crashes the bot."""
    from django.db import connection
    from django.db.utils import OperationalError

    needed = (
        'core_groqapikey',
        'core_messages',
        'core_stickersanya',
        'users_telegramuser',
        'users_limits',
        'users_subscribeplus',
        'axes_accessattempt',
    )

    try:
        tables = set(connection.introspection.table_names())
    except OperationalError:
        tables = set()

    if any(name not in tables for name in needed):
        raise SystemExit(
            'База данных ещё не создана, поэтому бот падает.\n\n'
            'В папке проекта выполните по порядку:\n'
            'python manage.py makemigrations\n'
            'python manage.py migrate\n'
        )


ensure_database_ready()


from aiogram import Bot, Dispatcher
from dotenv import load_dotenv



from bot.handlers import register_all_handlers




BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


token = (os.getenv('TOKEN') or '').strip()
if not token:
    raise SystemExit(
        "Заполните TOKEN в файле .env\n\n"
        "Пример:\n"
        "TOKEN=123456789:AAExampleTokenFromBotFather"
    )


async def main():
    bot = Bot(token=token)
    dp = Dispatcher()


    register_all_handlers(dp)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())