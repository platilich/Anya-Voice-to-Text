# --- models ---
from users.models import Limits
from bot_messages.models import LimitMessages, get_text



# --- function that checks whether the message can be processed ---
async def if_can_process(user_id, message):
    """
    getting user date.
        1. used_time - time already spent by the user.
        2. allowed = the number of available minutes per day depends on the tariff
    """

    used_time, allowed = await Limits.get_usage_for_profile(user_id)


    """
    function that checks if the date in the database differs from today's date:
        1. Change the date in the database to the current one
        2. Set the seconds used to 0
    """

    await Limits.maybe_reset(user_id)


    # --- if the time used is less than the allowed time, we allow ----
    if used_time <= allowed:
        return True



    # --- informing you that we cannot process it ---
    else:
        # --- send sticker ---

        sticker_file_id = 'CAACAgIAAxkBAAIBvWrTv6l-cN3DX2w_FqR-KE10qtMCAAJIrwAC-pahSkxOTB4PtFkjPQQ'
        await message.answer_sticker(sticker=sticker_file_id)


        # --- send message ---
        text = await get_text(model=LimitMessages, key='limit')
        text_ready = text.replace('{used_time}', used_time).replace('{allowed}', allowed)

        await message.answer(
            text=text_ready,
            parse_mode='HTML'
        )

        return False



# --- increasing the counter of minutes spent ---
async def increase_used(user_id, seconds_used):
    await Limits.spend_seconds(user_id, seconds_used)