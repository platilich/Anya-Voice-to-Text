from users.models import Stickers
from bot.logger import logger



async def send_sticker_with_anya(message, name_sticker):
    try:
        sticker_id = await Stickers.get_sticker(name_sticker)

        if sticker_id:
            await message.answer_sticker(sticker=sticker_id)

    except Exception as e:
        logger.info(f'Поле с стикером похоже не было заполненно или такого ID нет: {e}')