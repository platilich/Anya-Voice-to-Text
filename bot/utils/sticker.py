from core.models import StickersAnya
from bot.logger import logger



async def send(message, name_sticker):
    try:
        # --- attempt to get Sticker ID ---
        logger.info('sending a sticker')

        # --- getting sticker ID
        sticker_id = await StickersAnya.get_sticker(name_sticker)

        if sticker_id:
            # --- sending a sticker ---
            await message.answer_sticker(sticker=sticker_id)

        else:
            logger.info('Sticker ID not found')


    except Exception as e:
        logger.info(f'Something went wrong. function send: {e}')