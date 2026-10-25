# --- for reactions to messages ---
from aiogram.types import ReactionTypeEmoji

# --- for paths ---
from pathlib import Path
import os


# --- functions bot/ ---
from bot.logger import logger
from bot_messages.models import get_text
from bot.sticker import send


# --- model ErrorMessages ---
from bot_messages.models import ErrorMessages


# --- bot/handlers/this_file.py ---
TEMP_DIR = Path(__file__).resolve().parents[2] / "temp"




async def download_file(bot, message, file_obj):
    # --- for voice messages use .ogg, for video notes mp4
    ext = 'ogg' if message.voice else 'mp4'

    # --- creating directory for temporary files ---
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    path = str(TEMP_DIR / f"{message.from_user.id}_{message.message_id}.{ext}")


    # get_file only returns Telegram's path. The bytes are saved by download_file.
    file_info = await bot.get_file(file_obj.file_id)
    await bot.download_file(str(file_info.file_path), destination=path)


    logger.info(path)

    return path



# --- function for sending error messages to user ---
async def failed_message(message):
    # --- inform the user about the error ---
    # --- reaction emoji and sticker ---
    await message.react([ReactionTypeEmoji(emoji="😢")])
    await send(message, "oops")

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
        try:
            await bot.send_message(
                chat_id=int(admin_id),
                text=text,
                parse_mode="HTML",
            )

        except Exception as admin_err:
            logger.error(f"Failed to notify admin: {admin_err}")