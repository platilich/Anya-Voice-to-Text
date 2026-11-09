# --- models ---
from users.models import TelegramUser

from bot.middlewares.rejection_messages import send_more_than_fifteen_minutes

from bot.logger import logger




# --- function that checks whether the message can be processed ---
async def if_can_process(user_id, message, duration_voice_message):
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


    if duration_voice_message > 900:
        await send_more_than_fifteen_minutes(message)
        logger.info(f'voice too long | {user_id}')
        return True



    if await TelegramUser.not_enough_seconds(user_id, duration_voice_message):
        logger.info(f'not enough seconds, user: {user_id}')
        return True



    return False