from bot.logger import logger
from bot_messages.models import LimitMessages, get_text
from bot.keyboards.create_keyboard import keyboard_copy


async def send_more_than_fifteen_minutes(message):
    try:
        text = await get_text(model=LimitMessages, key='too_long')

        await message.answer(text)


    except Exception as e:
        logger.info(f'failed send too long message: {e}')




async def send_minutes_ended(message):
    user_id = message.from_user.id
    name = message.from_user.first_name

    logger.info(f'user {user_id} over limit')


    # --- send message ---
    text = await get_text(model=LimitMessages, key='limit')
    response = text.replace('{name}', str(name))

    keyboard = await keyboard_copy(f'https://t.me/anya_voice_to_text_bot?start={user_id}')

    await message.answer(
        text=response,
        parse_mode='HTML',
        reply_markup=keyboard
    )