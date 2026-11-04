from aiogram import Router, types
from aiogram.filters import Command

from bot.middlewares.filters import check_user
from bot.utils.sticker import send
from bot.logger import logger

# --- models ---
from bot_messages.models import get_text, StartMessages

# --- to send the name safety (html.escape(name)) ---
import html



router = Router(name='command_start')


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    name = message.from_user.first_name

    logger.info('got a command /start')

    # --- the function for updating user data will also return True if the user is banned ---
    if await check_user(message, duration_voice_message=None): # update, save, protect
        return


    await send(message, name_sticker='hello')

    text = await get_text(StartMessages, 'start_text')

    response = text.replace('{name}', html.escape(name))


    try:
        logger.info('attempt send message to user')
        await message.answer(response, parse_mode='HTML', disable_web_page_preview=True)

    except Exception as e:
        logger.info(f'failed send /start to {message.from_user.id}: {e}')