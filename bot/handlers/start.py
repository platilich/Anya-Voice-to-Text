from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from aiogram.types import FSInputFile


from bot_messages.models import get_text, StartMessages
from bot.middlewares.filters import check_user
from bot.logger import logger


from pathlib import Path
import html




router = Router(name='command_start')




@router.message(Command("start"))
async def cmd_start(message: types.Message, command: CommandObject):
    name = message.from_user.first_name
    friend_id = command.args


    logger.info('got a command /start')



    if await check_user(message=message, friend_id=friend_id):
        return


    # --- path ---
    text = await get_text(StartMessages, key='start_text')

    response = text.replace('{name}', html.escape(name))

    project_root = Path(__file__).resolve().parent.parent
    screen_file = project_root / "screens" / "instruction.jpeg"
    photo = FSInputFile(screen_file)



    try:

        await message.answer_photo(
            photo=photo,
            caption=response,
            parse_mode='HTML',
        )

    except Exception as e:
        logger.info(f'failed send /start to {message.from_user.id}: {e}')