from datetime import datetime, timedelta, timezone
import html
from aiogram.types import FSInputFile
from cachetools import TTLCache
from pathlib import Path

from bot.logger import logger

from users.models import TelegramUser
from core.models import Protection
from reference_links.models import get_texts_for_reference, get_count_minutes



rate_limit_cache = TTLCache(maxsize=10000, ttl=60)
pro_status = TTLCache(maxsize=1, ttl=180)


async def anti_bot(user_id, is_bot):
    if is_bot:
        await TelegramUser.change_status_banned(user_id, is_banned=True)
        return True

    else:
        return False




async def anti_flood(user_id):
    rest_seconds = await Protection.get_rest_time()
    rest = timedelta(seconds=rest_seconds)
    now = datetime.now(timezone.utc)
    last_message_time = rate_limit_cache[user_id]

    if last_message_time is not None and (now - last_message_time) < rest:
        return True

    rate_limit_cache[user_id] = now
    return False



def parse_referrer_id(raw_friend_id, user_id: int) -> int | None:
    if raw_friend_id is None:
        return None

    try:
        friend_id = int(raw_friend_id)

    except (TypeError, ValueError):
        return None

    if friend_id <= 0 or friend_id == user_id:
        return None

    return friend_id



async def check_user(**kwargs):
    message = kwargs.get('message')

    user_id = int(message.from_user.id)
    friend_id = parse_referrer_id(kwargs.get('friend_id'), user_id)
    name = message.from_user.first_name
    nickname = message.from_user.username
    is_bot = message.from_user.is_bot


    # --- skip flooded human messages before touching the database ---
    if not is_bot and await anti_flood(user_id):
        logger.info(f'user {user_id} flood, skip')
        return 'bad'



    user, created = await TelegramUser.save_or_update_user(user_id, name, nickname)



    if user.is_banned:
        logger.info(f'user {user_id} banned, skip')
        return 'bad'


    if not created:
        changed_fields = []
        if user.name != name:
            changed_fields.append("name")

        if user.nickname != nickname:
            changed_fields.append("nickname")

        if changed_fields:
            await user.asave(update_fields=changed_fields)


    # --- if the user is new and arrived via a referral link ---
    if friend_id is not None and created:
        logger.info(f"We issue: {user_id}, {friend_id} monthly subscriptions")

        await TelegramUser.increase_invited_users(friend_id)



        # --- add seconds new user, and friend which invited

        seconds_for_user = await get_count_minutes('count_minutes_new_user')
        seconds_for_owner = await get_count_minutes('count_minutes_for_owner_link')




        await TelegramUser.add_seconds(user_id, seconds=int(seconds_for_user))
        await TelegramUser.add_seconds(friend_id, seconds=int(seconds_for_owner))



        # --- sending a messages to friend_id---
        project_root = Path(__file__).resolve().parent.parent
        screen_file = project_root / "screens" / "free_minutes.jpeg"
        photo = FSInputFile(screen_file)


        # 2. your friend followed the link! Here are 3 minutes for you!
        for_owner_url = await get_texts_for_reference(key='ref_link_success_owner')

        response = for_owner_url.replace('{name}', html.escape(name))




        await message.bot.send_photo(
            chat_id=friend_id,
            photo=photo,
            caption=response,
            parse_mode='HTML'
        )


        return 'new'


    return False