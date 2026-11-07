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
    left_days_subscribe = await SubscribePlus.left_days_subscribe(user_id=user_id)


    # 2. Формируем заголовок (с экранированием HTML)
    profile_header = await get_text(ProfileMessages, 'header')
    profile_header = profile_header.replace('{name}', html.escape(name or "Пользователь"))


    # 3. Формируем статистику (приводим число к str)
    profile_statistic = await get_text(ProfileMessages, 'statistic')
    profile_statistic = profile_statistic.replace('{recognised}', str(all_time_recognised))


    # 5. Обрабатываем статус подписки
    if left_days_subscribe is None or left_days_subscribe < 0:
        variable_status = await get_text(ProfileMessages, key='variable_status_not_active')


    elif left_days_subscribe == 0:
        variable_status = await get_text(ProfileMessages, key='variable_status_end_today')


    else:
        # Активная подписка
        text = await get_text(ProfileMessages, key='variable_status_days_left')
        variable_status = text.replace('{days}', str(left_days_subscribe))




    status_subscribe = await get_text(ProfileMessages, key='text_status_subscribe')


    status_subscribe = status_subscribe.replace('{variable_status}', str(variable_status))



    profile_limit = await get_text(ProfileMessages, key='minutes_used_today')
    profile_limit = profile_limit.replace('{used_minutes}', str(used_minutes)).replace('{allowed_minutes}', allowed_minutes)
    about_limits = '⏳ The limits are updated every 24 hours'


    suggest = "🎁 You can get a free month of subscription!\n📋 Copy the link below and send it to a friend."

    # 7. Собираем сообщение
    profile_blocks = [
        profile_header,
        profile_statistic,
        profile_limit,
        about_limits,
        status_subscribe,
        suggest

    ]



    return "\n\n".join(profile_blocks)