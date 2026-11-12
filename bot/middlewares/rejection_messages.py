from bot.logger import logger
from bot_messages.models import LimitMessages, ErrorMessages, get_text
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




async def failed_downloaded_file(message):
    text = await get_text(model=ErrorMessages, key='failed_downloading')

    try:
        logger.error(
        "An error occurred, unable to download the user's message. Attempting to notify the user about the problem."
        )

        await message.answer(
            text=text,
            parse_mode='HTML'
        )


    except Exception as e:
        logger.error(f'Failed to send message to user: {e}')