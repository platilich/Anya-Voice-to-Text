from core.models import StickersAnya
from bot.logger import logger



async def send(message, name_sticker):
    try:
        sticker_id = await StickersAnya.get_sticker(name_sticker)

        if sticker_id:
            await message.answer_sticker(sticker=sticker_id)



    except Exception as e:
        logger.info(f'Поле с стикером похоже не было заполненно или такого ID стикера нет: {e}')