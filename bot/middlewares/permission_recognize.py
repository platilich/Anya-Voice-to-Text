# --- models ---
from users.models import TelegramUser

from bot.logger import logger
from bot.middlewares.rejection_messages import send_more_than_fifteen_minutes
from bot.keyboards.create_keyboard import keyboard_copy
from bot_messages.models import get_text, LimitMessages
import html



# --- function that checks whether the message can be processed ---
async def not_enough_minutes(message, user_id, duration_voice_message):
    """
    function that checks if the date in the database differs from today's date:
        1. Change the date in the database to the current one
        2. Set the seconds used to 0
    """

    """
    getting user date.
        1. used_time - time already spent by the user.
        2. allowed = the number of available minutes per day depends on the tariff
    """


    name = message.from_user.first_name


    if duration_voice_message > 900:
        logger.info(f'voice too long | {user_id}')
        await send_more_than_fifteen_minutes(message)
        return True



    if await TelegramUser.not_enough_seconds(user_id, duration_voice_message):
        logger.info(f'not enough seconds, user: {user_id}')
        # --- creating keyboard ---
        url = f'https://t.me/anya_voice_to_text_bot?start={user_id}'
        keyboard = await keyboard_copy(url)

        # --- getting a text for message from limits text ---
        text = await get_text(LimitMessages, key='limit')
        text = text.replace('{name}', html.escape(name or ''))

        await message.answer(
            text=text,
            parse_mode='HTML',
            reply_markup=keyboard
        )

        return True



    return False