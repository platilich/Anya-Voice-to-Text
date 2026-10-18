from aiogram import Router, types
from aiogram.filters import Command
from bot.utils.block_spam import usp
from datetime import datetime, timezone
import html

from users.models import TelegramUser, Limits, SubscribePlus
from bot.utils.send_sticker import send_sticker_with_anya

router = Router(name='command_profile')



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




@router.message(Command("profile"))
async def profile(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name


    if await usp(message): # update, save, protect
        return


    await send_sticker_with_anya(message, 'profile')



    user_data = await TelegramUser.get_statistic(user_id=user_id)
    user_data_limits = await Limits.get_data_about_user_limits(user_id=user_id)
    user_message_subscribe = await SubscribePlus.user_message_status_subscribe(user_id=user_id)
    allowed_per_hour = await SubscribePlus.get_allowed_processing_per_hour(user_id=user_id)

    reset_time = user_data_limits[1]
    minutes_left = get_reset_minutes(reset_time)


    if user_message_subscribe == 0:
        status_message_subscribe =  '⏰ <b>Your Plus subscription expires today!</b> Don\'t forget to renew it! ✨\n\n'

    elif user_message_subscribe is None:
        status_message_subscribe = '✨ <b>Want more limits?</b>\n🚀 Upgrade to Plus for 5х higher limits (50 req/hr)!\n👉 <b>/get_plus</b>'

    else:
        status_message_subscribe = f'⭐ <b>Plus Subscription:</b> {user_message_subscribe} days left\n\n'


    if minutes_left:
        limit_text = f'⏳ The limit will be updated in: {minutes_left} min.\n\n'


    elif minutes_left == 0:
        limit_text = (
            '⏳ The limit will reset in a minute, just wait a little longer.\n\n'
        )

    elif minutes_left is None:
        limit_text = f'Your limits per hour: {user_data_limits[0]}/{allowed_per_hour}\n\n'


    message_text = (
        f'Hey <b>{html.escape(name)}</b>! Here is everything I know about'
        ' you: 🎧\n\n'
        f'🆔 <b>Telegram ID:</b> <code>{user_id}</code>\n\n'
        '📊 <b>Your Activity:</b>\n'
        f' - Voice notes processed: <b>{user_data[0]}</b> 🎙️\n'
        f' - Video notes processed: <b>{user_data[1]}</b> 🎥\n\n'
        f'{limit_text}'
        f'{status_message_subscribe}'
        "\n\n<a href='https://github.com/platilich/NoteCircle'><b>GitHub</b></a>"
    )

    await message.answer(
        text=message_text, parse_mode='HTML', disable_web_page_preview=True
    )