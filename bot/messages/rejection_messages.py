from bot.logger import logger
from bot_messages.models import LimitMessages, ErrorMessages, get_text
from bot.keyboards.create_keyboard import keyboard_copy
import os
from aiogram.types import ReactionTypeEmoji
import html

from transcription.models import get_api_texts_limitation


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
        logger.error("An error occurred, unable to download the user's message. Attempting to notify the user about the problem.")

        await message.answer(
            text=text,
            parse_mode='HTML'
        )


    except Exception as e:
        logger.error(f'Failed to send message to user: {e}')





# --- function for sending error messages to user ---
async def failed_message(message):
    logger.info(f'send service unavailable | {message.from_user.id}')

    # --- inform the user about the error ---
    # --- reaction emoji and sticker ---
    await message.react([ReactionTypeEmoji(emoji="😢")])

    # --- send message about error ---
    text = await get_text(ErrorMessages, 'service_unavailable')
    await message.answer(text)




# --- function for sending problem with Groq API keys message to admin ---
async def notify_admin(bot):
    # --- extract admin id from .env ---
    admin_id = os.getenv("ADMIN_ID")


    # --- send message to inform admin about problem with Groq API keys ---
    text = await get_api_texts_limitation('admin_no_keys')

    if admin_id:
        logger.info(f'notify admin {admin_id}')
        try:
            await bot.send_message(
                chat_id=int(admin_id),
                text=text,
                parse_mode="HTML",
            )

        except Exception as admin_err:
            logger.error(f'failed notify admin: {admin_err}')

    else:
        logger.info('no ADMIN_ID, cant notify')




async def send_message_not_enough_seconds(message):
    user_id = message.from_user.id
    name = message.from_user.first_name


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




async def gemini_limits(message):
    text = await get_api_texts_limitation('gemini_limits_ended')

    await message.answer(
        text=text,
        parse_mode='HTML'
    )


    admin_id = os.getenv("ADMIN_ID")

    if admin_id:
        logger.info(f'notify admin {admin_id}')
        text = await get_api_texts_limitation('gemini_limits_ended_for_admin')

        try:
            await message.bot.send_message(
                chat_id=int(admin_id),
                text=text,
                parse_mode="HTML",
            )


        except Exception as admin_err:
            logger.error(f'failed notify admin: {admin_err}')

    else:
        logger.info('no ADMIN_ID, cant notify')




async def send_message_little_longer(message):
    text = await get_api_texts_limitation('new_attempt_recognise')

    await message.answer(
        text=text,
        parse_mode='HTML'
    )