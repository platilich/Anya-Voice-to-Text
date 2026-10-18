from users.models import TelegramUser




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