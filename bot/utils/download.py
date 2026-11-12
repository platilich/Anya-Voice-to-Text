from aiogram.types import ReactionTypeEmoji
from pathlib import Path
import os

from bot.logger import logger
from bot_messages.models import get_text
from bot_messages.models import ErrorMessages


# --- bot/handlers/this_file.py ---
TEMP_DIR = Path(__file__).resolve().parents[2] / "temp"




async def download_file(bot, message, file_obj):
    # --- for voice messages use .ogg, for video notes mp4 ---

    ext = 'ogg' if message.voice else 'mp4'
    logger.info(f'downloading {ext} | {message.from_user.id}')

    try:
        logger.info('creating directory...')
        TEMP_DIR.mkdir(parents=True, exist_ok=True)


    except Exception as e:
        logger.error(f'directory already created: {e}')


    path = str(TEMP_DIR / f"{message.from_user.id}_{message.message_id}.{ext}")


    try:
        logger.info('downloading a file...')
        file_info = await bot.get_file(file_obj.file_id)
        await bot.download_file(str(file_info.file_path), destination=path)

        return path


    except Exception as e:
        logger.error(f'error during downloading a file: {e}')
        os.remove(path)

        return None







# --- function for sending error messages to user ---
async def failed_message(message):
    logger.info(f'send service unavailable | {message.from_user.id}')

    # --- inform the user about the error ---
    # --- reaction emoji and sticker ---
    await message.react([ReactionTypeEmoji(emoji="😢")])

    # --- send message about error ---
    text = await get_text(ErrorMessages, 'service_unavailable')
    await message.answer(text)




# --- function for sending problem with Groq API keys message to admin ---
async def notify_admin(bot):
    # --- extract admin id from .env ---
    admin_id = os.getenv("ADMIN_ID")


    # --- send message to inform admin about problem with Groq API keys ---
    text = await get_text(model=ErrorMessages, key='admin_no_groq_keys')

    if admin_id:
        logger.info(f'notify admin {admin_id}')
        try:
            await bot.send_message(
                chat_id=int(admin_id),
                text=text,
                parse_mode="HTML",
            )

        except Exception as admin_err:
            logger.error(f'failed notify admin: {admin_err}')

    else:
        logger.info('no ADMIN_ID, cant notify')