from datetime import datetime, timedelta, timezone
import html
from aiogram.types import FSInputFile
from cachetools import TTLCache
from pathlib import Path

from bot.logger import logger
from bot.middlewares.permission_recognize import if_can_process
from bot.middlewares.rejection_messages import send_more_than_fifteen_minutes
from bot_messages.models import get_text, ReferenceTexts, LimitMessages
from bot.keyboards.create_keyboard import keyboard_copy

from users.models import ReferenceLinks, TelegramUser
from core.models import Protection


from toggles.models import ShopStatus





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
    last_message_time = rate_limit_cache.get(user_id)

    if last_message_time is not None and (now - last_message_time) < rest:
        return True

    rate_limit_cache[user_id] = now
    return False





async def protection_for_voice_handler(user_id: int, duration_voice_message: int):
    return await if_can_process(user_id, duration_voice_message)



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
    duration_voice_message = kwargs.get('duration_voice_message')

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
            changed_fields.append(user.name)

        if user.nickname != nickname:
            changed_fields.append(user.nickname)

        if changed_fields:
            await user.asave(update_fields=changed_fields)

    if created:
        await ReferenceLinks.create_new_link(user_id)


    # --- if the user is new and arrived via a referral link ---
    if friend_id is not None and created:
        logger.info(f"We issue: {user_id}, {friend_id} monthly subscriptions")

        await ReferenceLinks.increase_invited_users(user_id)

        # --- add seconds new user, and friend which invited
        await TelegramUser.add_seconds(user_id, seconds=180)
        await TelegramUser.add_seconds(friend_id, seconds=180)



        # --- sending a messages to friend_id---
        project_root = Path(__file__).resolve().parent.parent
        screen_file = project_root / "screens" / "free_minutes.jpeg"
        photo = FSInputFile(screen_file)


        # 2. Your friend followed the link! Here are 3 minutes for you!
        for_owner_url = await get_text(ReferenceTexts, key='ref_link_success_owner')

        response = for_owner_url.replace('{name}', html.escape(name))




        await message.bot.send_photo(
            chat_id=friend_id,
            photo=photo,
            caption=response,
            parse_mode='HTML'
        )


        return 'new'


    if duration_voice_message is not None:
        if await protection_for_voice_handler(user_id, duration_voice_message):
            if duration_voice_message > 900:
                await send_more_than_fifteen_minutes(message)
                return True

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
            return 'bad'


    elif message.text:
        command = message.text.split(maxsplit=1)[0].split('@', 1)[0]
        if command == '/shop':
            status = await ShopStatus.get_status_shop()
            logger.info(f'магазин не работает: {status}')
            return status



    return False