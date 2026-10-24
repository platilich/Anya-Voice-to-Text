from users.models import Limits

from bot_messages.models import LimitMessages, get_text


async def if_can_process(user_id, message):
    free_minutes, allowed = await Limits.get_usage_for_profile(user_id)

    await Limits.maybe_reset(user_id)

    if free_minutes <= allowed:
        return True


    else:
        sticker_file_id = 'CAACAgIAAxkBAAIBvWrTv6l-cN3DX2w_FqR-KE10qtMCAAJIrwAC-pahSkxOTB4PtFkjPQQ'
        await message.answer_sticker(sticker=sticker_file_id)


        text = await get_text(model=LimitMessages, key='limit')


        text_ready = text.replace('{free_minutes}', free_minutes).replace('{allowed}', allowed)

        await message.answer(
            text=text_ready,
            parse_mode='HTML'
        )

        return False # лимиты превышенны




async def increase_used(user_id, seconds_used):
    await Limits.spend_seconds(user_id, seconds_used)