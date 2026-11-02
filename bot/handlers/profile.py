from aiogram import Router, types
from aiogram.filters import Command

from bot.utils.sticker import send
from bot.middlewares.filters import check_user
from bot.utils import profile_form
from bot.logger import logger


router = Router(name='command_profile')



@router.message(Command("profile"))
async def profile(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name

    logger.info('got a command /profile')

    # --- the function for updating user data will also return True if the user is banned ---
    if await check_user(message, None):
        return


    await send(message, 'profile')


    # --- function for generating a message for /profile ---
    message_text = await profile_form.profile_message(user_id, name)


    logger.info('attempt send /profile')

    await message.answer(
        text=message_text, parse_mode='HTML', disable_web_page_preview=True
    )