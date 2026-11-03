from bot.logger import logger
from bot_messages.models import LimitMessages, get_text
from bot.utils.sticker import send



async def send_more_than_fifteen_minutes(message):
    try:
        await send(message, name_sticker='limits')
        text = await get_text(model=LimitMessages, key='too_long')

        await message.answer(text)

    except Exception as e:
        logger.info(f'failed send too long message: {e}')



async def send_duration_longer_left_min(message, used_time, allowed):
    user_id = message.from_user.id

    logger.info(f'user {user_id} over limit {used_time}/{allowed}')
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



async def send_minutes_ended(message, used_time, allowed):
    user_id = message.from_user.id

    logger.info(f'user {user_id} over limit {used_time}/{allowed}')
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