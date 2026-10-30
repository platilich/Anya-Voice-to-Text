from aiogram import Router, types
from aiogram.filters import Command

# --- bot/ ---
from bot.utils.sticker import send
from bot.middlewares.filters import check_user
from bot.utils import profile_form

router = Router(name='command_profile')



@router.message(Command("profile"))
async def profile(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name


    # --- the function for updating user data will also return True if the user is banned ---
    if await check_user(message, None):
        return


    # --- sending a sticker --
    await send(message, 'profile')


    # --- function for generating a message for /profile ---
    message_text = await profile_form.profile_message(user_id, name)


    # --- sending a message ---
    await message.answer(
        text=message_text, parse_mode='HTML', disable_web_page_preview=True
    )