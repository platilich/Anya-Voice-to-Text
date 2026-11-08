from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import FSInputFile

from pathlib import Path

from bot.middlewares.filters import check_user
from bot.utils import profile_form
from bot.logger import logger
from bot.keyboards.create_keyboard import keyboard_copy

router = Router(name='command_profile')



@router.message(Command("profile"))
async def profile(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name

    logger.info('got a command /profile')



    # --- the function for updating user data will also return True if the user is banned ---
    if await check_user(message=message):
        return



    # --- function for generating a message for /profile ---
    message_text = await profile_form.profile_message(user_id, name)

    keyboard = await keyboard_copy(f'https://t.me/anya_voice_to_text_bot?start={user_id}')



    # --- path ---
    project_root = Path(__file__).resolve().parent.parent
    screen_file = project_root / "screens" / "profile.jpeg"
    photo = FSInputFile(screen_file)



    await message.answer_photo(
        photo=photo,
        caption=message_text,
        parse_mode='HTML',
        reply_markup=keyboard,
        disable_web_page_preview=True
    )