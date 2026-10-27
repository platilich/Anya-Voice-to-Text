from users.models import TelegramUser
from bot_messages.models import LimitMessages, get_text


from bot.middlewares.limits import if_can_process
from bot.utils.sticker import send
from bot.logger import logger




async def usp(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    nickname = message.from_user.username
    is_bot = message.from_user.is_bot


    if is_bot:
        await TelegramUser.save_or_update_user(user_id, name, nickname)
        await TelegramUser.change_status_banned(user_id, True)
        return True


    if await TelegramUser.banned_user(user_id):
        return True


    await TelegramUser.save_or_update_user(user_id, name, nickname)

    return False




async def to_long(message):
    try:
        await send(message, name_sticker='limits')
        text = await get_text(model=LimitMessages, key='too_long')

        await message.answer(text)

    except Exception as e:
        logger.info(f'error during sending message to user: {e}')





async def usp_on_voice(message, time_voice_message):
    user_id = message.from_user.id

    if await usp(message):
        return True


    if not await if_can_process(user_id, message):
        return True


    if time_voice_message > 900:
        await to_long(message)
        return True


    return False