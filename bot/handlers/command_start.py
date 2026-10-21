from aiogram import Router, types
from aiogram.filters import Command
from bot.utils.block_spam import usp
from bot.utils.send_sticker import send_sticker_with_anya, send_message


router = Router(name='command_start')


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    if await usp(message): # update, save, protect
        return


    await send_sticker_with_anya(message, 'hello')
    await send_message(message, 'start')