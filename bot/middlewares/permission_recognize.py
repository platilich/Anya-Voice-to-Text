# --- models ---
from users.models import TelegramUser

from bot.logger import logger
from messages.rejection_messages import send_more_than_fifteen_minutes, send_message_not_enough_seconds


# --- function that checks whether the message can be processed ---
async def not_enough_minutes(message, duration_voice_message):
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


    user_id = message.from_user.id

    if duration_voice_message > 900:
        logger.info(f'voice too long | {user_id}')
        await send_more_than_fifteen_minutes(message)
        return True



    if await TelegramUser.not_enough_seconds(user_id, duration_voice_message):
        logger.info(f'not enough seconds, user: {user_id}')
        await send_message_not_enough_seconds(message)
        return True



    return False