from time import time
from users.models import TelegramUser



last_message_time = {}


def is_spam(user_id):
    if not user_id:
        return True

    current_time = time()
    last = last_message_time.get(user_id)
    last_message_time[user_id] = current_time

    return last is not None and current_time - last < 2.0




async def usp(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    nickname = message.from_user.username
    is_bot = message.from_user.is_bot


    if await TelegramUser.banned_user(user_id):
        return True

    if is_spam(user_id):
        return True


    if is_bot:
        return True


    await TelegramUser.save_or_update_user(user_id, name, nickname)


    return False