from aiogram import Router, types
from aiogram.filters import Command
from bot.utils.block_spam import usp
from bot import profile_form

from bot.utils.send_sticker import send_sticker_with_anya



router = Router(name='command_profile')



@router.message(Command("profile"))
async def profile(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name


    if await usp(message): # update, save, protect
        return


    await send_sticker_with_anya(message, 'profile')

    message_text = await profile_form.profile_message(user_id, name)


    await message.answer(
        text=message_text, parse_mode='HTML', disable_web_page_preview=True
    )