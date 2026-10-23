from users.models import Limits, SubscribePlus
from datetime import datetime, timezone




async def if_process_limit_allowed(user_id, message):
    processed_per_hour = await Limits.get_processed_per_hour(user_id)
    reset_time = await Limits.get_reset_time(user_id)


    get_allowed_processing_per_hour = await SubscribePlus.get_allowed_processing_per_hour(user_id)

    current_time = datetime.now(timezone.utc)

    if processed_per_hour < get_allowed_processing_per_hour and (reset_time is None or reset_time < current_time):
        await Limits.reset_limit_time(user_id)
        return True # обрабатываем юзера лимиты еще не превысил


    else:
        sticker_file_id = 'CAACAgIAAxkBAAIBvWrTv6l-cN3DX2w_FqR-KE10qtMCAAJIrwAC-pahSkxOTB4PtFkjPQQ'
        await message.answer_sticker(sticker=sticker_file_id)

        if reset_time is None:
            await Limits.set_reset_time(user_id)

        await Limits.reset_processed_per_hour(user_id)

        reset_time = await Limits.get_reset_time(user_id)

        current_time = datetime.now(timezone.utc)
        left_time = reset_time - current_time

        minutes_left = int(left_time.total_seconds() // 60)


        text = (
            f"📊 <b>Limits:</b> {get_allowed_processing_per_hour}/{get_allowed_processing_per_hour} requests left\n"
            f"⏳ <b>Reset in:</b> {minutes_left} min\n\n"
            f"⭐ <b>Upgrade to Plus</b> for higher limits!\n"
            '👉 <b>/get_plus</b>'
        )


        await message.answer(
            text=text,
            parse_mode='HTML'
        )

        return False # лимиты превышенны




async def increase_processed(user_id):
    await Limits.increase_processed_per_hour(user_id)