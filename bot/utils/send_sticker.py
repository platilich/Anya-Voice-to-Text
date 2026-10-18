from core.models import StickersAnya, Messages
from bot.logger import logger
import html



async def send_message(message, message_name):
    try:
        name = html.escape(message.from_user.first_name or "Friend")

        message_text = await Messages.get_message_text(message_name)

        if name in message_text:
            message_text = message_text.replace('name', name)

        await message.answer(
            text=message_text,
            parse_mode="HTML",
            disable_web_page_preview=True
        )

    except Exception as e:
        logger.error(f'Поле с сообщением похоже не было заполненно или такого ID сообщения нет: {e}')


async def send_sticker_with_anya(message, name_sticker):
    try:
        sticker_id = await StickersAnya.get_sticker(name_sticker)

        if sticker_id:
            await message.answer_sticker(sticker=sticker_id)



    except Exception as e:
        logger.info(f'Поле с стикером похоже не было заполненно или такого ID стикера нет: {e}')