from pathlib import Path
import os

from bot.logger import logger

from utils.convert import conver_to_ogg


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

        if ext == 'mp4':
            path = await conver_to_ogg(path)


        return path


    except Exception as e:
        logger.error(f'error during downloading a file: {e}')

        try:
            logger.info(f'attempt to remove a file: {path}')
            os.remove(path)

        except Exception as e:
            logger.info(f'file not found: {e}')

        return None