from datetime import datetime, timezone, timedelta
from cachetools import TTLCache


from bot.middlewares.permission_recognize import if_can_process



# --- models ---
from users.models import TelegramUser
from bot_messages.models import LimitMessages, get_text


from core.models import get_rest_time



from bot.utils.sticker import send
from bot.logger import logger




seconds = 2.0


async def init_rest_time():
    global seconds

    seconds = await get_rest_time()




rate_limit_cache = TTLCache(maxsize=10000, ttl=60)
rest = timedelta(seconds=seconds)





async def to_long(message):
    try:
        await send(message, name_sticker='limits')
        text = await get_text(model=LimitMessages, key='too_long')

        await message.answer(text)

    except Exception as e:
        logger.info(f'error during sending message to user: {e}')




async def anti_bot(user_id, is_bot):

    if is_bot:
        await TelegramUser.change_status_banned(user_id, True)
        return True




async def anti_flood(user_id):
    now = datetime.now(timezone.utc)
    last_message_time = rate_limit_cache.get(user_id)

    # --- if the last message is less than 2 seconds, we do not respond ---
    if last_message_time is not None and (now - last_message_time) < rest:
        return True

    # --- update time last message ---
    rate_limit_cache[user_id] = now




async def check_user(message, duration_voice_message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    nickname = message.from_user.username
    is_bot = message.from_user.is_bot

    await TelegramUser.save_or_update_user(user_id, name, nickname)


    if await anti_bot(user_id, is_bot):
        return True


    if await TelegramUser.banned_user(user_id):
        return True


    if await anti_flood(user_id):
        return True


    if duration_voice_message:
        if not await if_can_process(user_id, message):
            return True

        if duration_voice_message > 900:
            await to_long(message)
            return True



    return False