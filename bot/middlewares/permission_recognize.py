# --- models ---
from users.models import Limits

from bot.middlewares.rejection_messages import (send_more_than_fifteen_minutes,
                                send_duration_longer_left_min,
                                send_minutes_ended)

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

    used_time, allowed = await Limits.get_used_and_max_allowed(user_id)



    if duration_voice_message > 900:
        await send_more_than_fifteen_minutes(message)
        logger.info(f'voice too long | {user_id}')
        return True



    if used_time + duration_voice_message > allowed:
        # --- a notification stating that the available daily minute allowance is insufficient to process this message ---
        await send_duration_longer_left_min(message, duration_voice_message)
        return True


    # --- if the time used exceeds the allowed time ----
    if used_time > allowed:
        await send_minutes_ended(message, used_time, allowed)
        return True




    return False