from users.models import Limits, SubscribePlus, TelegramUser
from core.models import Messages
from datetime import datetime, timezone
import html


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

    # Возвращаем минимум 1 минуту, чтобы не писать "0 min"
    return max(1, minutes_left)



async def profile_message(user_id, name):
    all_time_recognised = await TelegramUser.get_statistic(user_id=user_id)
    user_data_limits = await Limits.get_data_about_user_limits(user_id=user_id)
    user_message_subscribe = await SubscribePlus.user_message_status_subscribe(user_id=user_id)
    get_processed_per_hour = await Limits.get_processed_per_hour(user_id=user_id)
    get_allowed_per_hour = await SubscribePlus.get_allowed_processing_per_hour(user_id=user_id)


    reset_time = user_data_limits[1]
    minutes_left = get_reset_minutes(reset_time)


    profile_header = await Messages.get_message_text('profile_header')
    profile_statistic = await Messages.get_message_text('profile_statistic')


    profile_limit = await Messages.get_message_text('profile_limit')



    # --- profile status subscribe ---
    profile_status_subscribe = await Messages.get_message_text('profile_status_subscribe')

    if user_message_subscribe == 0:
        profile_status_subscribe = await Messages.get_message_text('profile_status_subscribe_ending_today')

    elif user_message_subscribe is None:
        profile_status_subscribe = await Messages.get_message_text('profile_status_no_subscribe')




    limits_reset_in = await Messages.get_message_text('the_limits_will_updated_for')

    if minutes_left == 0:
        limits_reset_in = await Messages.get_message_text('the_limits_will_updated_now')


    elif minutes_left is None:
        limits_reset_in = None





    if '{name}' in profile_header:
        profile_header = profile_header.replace('{name}', html.escape(name))



    profile_statistic = profile_statistic.replace('{recognised}', str(all_time_recognised[0]))

    profile_limit = profile_limit.replace(
        '{recognised}', str(get_processed_per_hour)).replace('{maximum_allowed}', str(get_allowed_per_hour))

    profile_blocks = [
        profile_header,
        profile_statistic,
        profile_limit,
    ]


    if limits_reset_in:
        profile_blocks.append(limits_reset_in)


    profile_blocks.append(profile_status_subscribe)


    return "\n\n".join(profile_blocks)