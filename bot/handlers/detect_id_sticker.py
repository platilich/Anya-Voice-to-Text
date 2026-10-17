from aiogram import F, Router
from aiogram.types import Message


router = Router(name='detect_id_sticker')



@router.message(F.sticker)
async def get_sticker_id(message: Message):
    sticker_id = message.sticker.file_id
    await message.answer(
      f'📦 <b>Sticker File ID:</b>\n`{sticker_id}`', parse_mode='HTML'
    )