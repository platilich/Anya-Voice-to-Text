from core.models import StickersAnya
from bot.logger import logger



async def send(message, name_sticker):
    try:
        # --- attempt to get sticker ID ---
        logger.info(f'sending sticker {name_sticker}')

        # --- getting sticker ID
        sticker_id = await StickersAnya.get_sticker(name_sticker)

        if sticker_id:
            # --- sending a sticker ---
            await message.answer_sticker(sticker=sticker_id)

        else:
            logger.info(f'sticker {name_sticker} not found')


    except Exception as e:
        logger.info(f'failed send sticker {name_sticker}: {e}')