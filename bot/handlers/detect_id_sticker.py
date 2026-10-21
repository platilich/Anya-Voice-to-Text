from aiogram import F, Router
from aiogram.types import Message
from core.models import Messages
from bot.utils.block_spam import usp

router = Router(name='detect_id_sticker')



@router.message(F.sticker)
async def get_sticker_id(message: Message):
    if await usp(message):
        return


    sticker_id = message.sticker.file_id


    message_text = await Messages.get_message_text('sticker_file_id')

    answer = message_text.replace('{sticker_id}', sticker_id)


    await message.answer(
        text=answer, parse_mode='HTML'
    )