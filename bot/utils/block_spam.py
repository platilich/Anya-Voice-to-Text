from time import time
from bot.db import Users



db = Users()
last_message_time = {}


def is_spam(user_id):
    if not user_id:
        return True

    current_time = time()
    last = last_message_time.get(user_id)
    last_message_time[user_id] = current_time

    return last is not None and current_time - last < 2.0




def usp(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    nickname = message.from_user.username
    is_bot = message.from_user.is_bot

    if db.is_banned(user_id):
        return True


    if is_spam(user_id):
        return True


    if is_bot:
        return True


    db.add_user(user_id, name, nickname)


    return False