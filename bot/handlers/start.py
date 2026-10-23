import html

from aiogram import Router, types
from aiogram.filters import Command

from bot.utils.block_spam import usp
from bot.sticker import send
from bot_messages.models import get_text, StartMessages


router = Router(name='command_start')


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    name = message.from_user.first_name


    if await usp(message): # update, save, protect
        return


    await send(message, 'hello')



    text = await get_text(StartMessages, 'start_text')
    response = text.replace('{name}', html.escape(name))



    await message.answer(response, parse_mode='HTML', disable_web_page_preview=True)