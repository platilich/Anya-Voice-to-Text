# --- models ---
from users.models import TelegramUser
from core.models import get_rest_time


# --- bot/ ---
from bot.logger import logger
from bot.middlewares.permission_recognize import if_can_process


from cachetools import TTLCache
from datetime import datetime, timezone, timedelta


from users.models import Limits, SubscribePlus



rate_limit_cache = TTLCache(maxsize=10000, ttl=60)




async def anti_bot(user_id, is_bot):
    if is_bot:
        await TelegramUser.change_status_banned(user_id, True)
        return True

    else:
        return False




async def anti_flood(user_id):
    rest_seconds = await get_rest_time()

    rest = timedelta(seconds=rest_seconds)


    now = datetime.now(timezone.utc)
    last_message_time = rate_limit_cache.get(user_id)

    # --- if the last message is less than 2 seconds, we do not respond ---
    if last_message_time is not None and (now - last_message_time) < rest:
        return True

    # --- update time last message ---
    rate_limit_cache[user_id] = now




async def update_data(user_id):
    await SubscribePlus.check_subscribe(user_id) # --- if the subscription has expired, we remove is_plus ---
    await Limits.reset_daily_seconds_if_new_day(user_id)  # --- if it’s a new day, we discard the old limits ---



async def check_user(message, duration_voice_message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    nickname = message.from_user.username
    is_bot = message.from_user.is_bot

    await TelegramUser.save_or_update_user(user_id, name, nickname)


    if await anti_bot(user_id, is_bot):
        logger.info(f'user {user_id} is bot, skip')
        return True


    if await TelegramUser.banned_user(user_id):
        logger.info(f'user {user_id} banned, skip')
        return True


    if await anti_flood(user_id):
        logger.info(f'user {user_id} flood, skip')
        return True



    await update_data(user_id)


    if duration_voice_message:
        if await if_can_process(user_id, message, duration_voice_message):
            return True


    return False