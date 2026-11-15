from datetime import datetime, timezone
import html


from bot_messages.models import (
    ProfileMessages,
    get_text,
)

from users.models import TelegramUser


async def profile_message(user_id: int, name: str) -> str:
    # 1. Получаем данные из БД
    all_time_recognised = await TelegramUser.get_statistic(user_id=user_id)
    left_seconds = await TelegramUser.get_usage_for_profile(user_id=user_id)

    minutes, seconds = divmod(max(0, int(left_seconds)), 60)

    # 2. Формируем заголовок (с экранированием HTML)
    profile_header = await get_text(ProfileMessages, 'header')
    profile_header = profile_header.replace('{name}', html.escape(name or "Пользователь"))


    # 3. Формируем статистику (приводим число к str)
    profile_statistic = await get_text(ProfileMessages, 'statistic')
    profile_statistic = profile_statistic.replace('{recognised}', str(all_time_recognised))

    minutes_left_today = await get_text(ProfileMessages, key='left_seconds')
    minutes_left_today = minutes_left_today.replace('{left_seconds}', f'{minutes}:{seconds:02d} minutes')

    about_limits = await get_text(ProfileMessages, key='about_limits')
    suggest = await get_text(ProfileMessages, key='text_suggest_invite_friend')


    # 7. Собираем сообщение
    profile_blocks = [
        profile_header,
        profile_statistic,
        minutes_left_today,
        about_limits,
        suggest

    ]



    return "\n\n".join(profile_blocks)