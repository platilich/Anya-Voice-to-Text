from datetime import datetime, timezone
import html



from bot_messages.models import (
    ProfileMessages,
    SubscriptionStatusMessages,
    get_text,
)


from users.models import Limits, SubscribePlus, TelegramUser



def get_reset_minutes(reset_datetime) -> int | None:
    if not reset_datetime:
        return None

    now = datetime.now(timezone.utc)

    # Если время сброса уже прошло
    if reset_datetime <= now:
        return None

    # Высчитываем разницу в минутах
    diff = reset_datetime - now
    minutes_left = int(diff.total_seconds() // 60)

    # Если сброс меньше чем через минуту, но еще не наступил
    return max(1, minutes_left)


async def profile_message(user_id: int, name: str) -> str:
    # 1. Получаем данные из БД
    all_time_recognised = await TelegramUser.get_statistic(user_id=user_id)
    used_minutes, allowed_minutes = await Limits.get_usage_for_profile(user_id=user_id)
    user_message_subscribe = await SubscribePlus.user_message_status_subscribe(user_id=user_id)


    # 2. Формируем заголовок (с экранированием HTML)
    profile_header = await get_text(ProfileMessages, 'header')
    profile_header = profile_header.replace('{name}', html.escape(name or "Пользователь"))


    # 3. Формируем статистику (приводим число к str)
    profile_statistic = await get_text(ProfileMessages, 'statistic')
    recognised_val = all_time_recognised[0] if all_time_recognised else 0
    profile_statistic = profile_statistic.replace('{recognised}', str(recognised_val))


    # 5. Обрабатываем статус подписки
    if user_message_subscribe is None or user_message_subscribe < 0:
        # У вас нет подписки
        profile_status_subscribe = await get_text(SubscriptionStatusMessages, 'no_subscription')


    elif user_message_subscribe == 0:
        # Заканчивается сегодня
        profile_status_subscribe = await get_text(SubscriptionStatusMessages, 'ending_today')


    else:
        # Активная подписка
        profile_status_subscribe = await get_text(SubscriptionStatusMessages, 'active_plus')
        profile_status_subscribe = profile_status_subscribe.replace('{left_days}', str(user_message_subscribe))



    profile_limit = f'🕓 Minutes used today: {used_minutes}/{allowed_minutes}'
    about_limits = '⏳ The limits are updated every 24 hours'


    # 7. Собираем сообщение
    profile_blocks = [
        profile_header,
        profile_statistic,
        profile_limit,
        about_limits

    ]




    profile_blocks.append(profile_status_subscribe)

    return "\n\n".join(profile_blocks)