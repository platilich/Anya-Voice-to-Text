from aiogram import Router, types
from aiogram.filters import Command

# --- bot/ ---
from bot.utils.block_spam import usp
from bot.sticker import send

# --- models ---
from bot_messages.models import get_text, StartMessages

# --- to send the name safety (html.escape(name)) ---
import html



router = Router(name='command_start')


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    name = message.from_user.first_name


    # --- the function for updating user data will also return True if the user is banned ---
    if await usp(message): # update, save, protect
        return


    # --- send a sticker hello ---
    await send(message, 'hello')


    # --- get from database text for message ---
    text = await get_text(StartMessages, 'start_text')

    # --- replace {name} to real name
    response = text.replace('{name}', html.escape(name))


    # --- send answer to user ---
    await message.answer(response, parse_mode='HTML', disable_web_page_preview=True)