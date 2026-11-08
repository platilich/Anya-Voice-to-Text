# --- models ---
from datetime import datetime, timedelta, timezone

from cachetools import TTLCache

from bot.logger import logger
from bot.middlewares.permission_recognize import if_can_process
from bot_messages.models import SubscriptionPlusMessages, get_text
from core.models import get_rest_time, CommandGetProStatus
from users.models import Limits, ReferenceLinks, SubscribePlus, TelegramUser




rate_limit_cache = TTLCache(maxsize=10000, ttl=60)
pro_status = TTLCache(maxsize=1, ttl=180)



async def is_work_command():
    logger.info('function is_work_command')

    status = await CommandGetProStatus.get_status_command_get_pro()

    logger.info(f'status commandgetprostatus: {status}')
    logger.info(f"||||||||||||| {status } |||||||||||||")
    return status




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

    if last_message_time is not None and (now - last_message_time) < rest:
        return True

    rate_limit_cache[user_id] = now
    return False



async def update_data(user_id):
    await SubscribePlus.check_subscribe(user_id)
    await Limits.reset_daily_seconds_if_new_day(user_id)



async def protection_for_voice_handler(message, user_id: int, duration_voice_message: int):
    await update_data(user_id)
    return await if_can_process(user_id, message, duration_voice_message)




async def check_user(**kwargs):
    message = kwargs.get('message')
    friend_id = kwargs.get('friend_id')
    duration_voice_message = kwargs.get('duration_voice_message')

    user_id = message.from_user.id
    name = message.from_user.first_name
    nickname = message.from_user.username
    is_bot = message.from_user.is_bot


    # --- skip flooded human messages before touching the database ---
    if not is_bot and await anti_flood(user_id):
        logger.info(f'user {user_id} flood, skip')
        return True


    user, created = await TelegramUser.objects.aget_or_create(
        user_id=user_id,
        defaults={'name': name, 'nickname': nickname},
    )


    if user.is_banned:
        logger.info(f'user {user_id} banned, skip')
        return True


    if not created:
        changed_fields = []
        if user.name != name:
            user.name = name
            changed_fields.append('name')

        if user.nickname != nickname:
            user.nickname = nickname
            changed_fields.append('nickname')

        if changed_fields:
            await user.asave(update_fields=changed_fields)

    if created:
        await ReferenceLinks.create_new_link(user_id)


    # --- if the user is new and arrived via a referral link ---
    if friend_id is not None and friend_id != user_id and created:
        logger.info(f"We issue: {user_id}, {friend_id} monthly subscriptions")

        await ReferenceLinks.increase_invited_users(user_id, friend_id)
        await SubscribePlus.give_subscribe(user_id)
        await SubscribePlus.give_subscribe(friend_id)


        for_new_user = await get_text(SubscriptionPlusMessages, key='ref_link_success_new_user')
        for_owner_url = await get_text(SubscriptionPlusMessages, key='ref_link_success_owner')
        await message.bot.send_message(user_id, text=for_new_user)
        await message.bot.send_message(friend_id, text=for_owner_url)



    if duration_voice_message is not None:
        if await protection_for_voice_handler(message, user_id, duration_voice_message):
            return True


    elif message.text:
        command = message.text.split(maxsplit=1)[0].split('@', 1)[0]
        if command == '/profile':
            await update_data(user_id)


    return False