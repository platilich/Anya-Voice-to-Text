from aiogram import Router, F, Bot, types
from aiogram.types import ReactionTypeEmoji

import html
import os
from pathlib import Path

from users.models import Limits


from users.models import TelegramUser


from bot.utils.limits import if_can_process, increase_used
from bot.utils.block_spam import usp
from bot.utils.cleanup import remove_temp_files
from bot.utils.audio_recognation import recognize, AllGroqKeysFailedError
from bot.logger import logger
from dotenv import load_dotenv



from bot_messages.models import LimitMessages
from bot.sticker import send
from bot_messages.models import get_text


load_dotenv()


# bot/handlers/this_file.py
TEMP_DIR = Path(__file__).resolve().parents[2] / "temp"


router = Router(name='handler_video')



async def to_long(message):
    try:
        await send(message, name_sticker='limits')
        text = await get_text(model=LimitMessages, key='too_long')

        await message.answer(text)

    except Exception as e:
        logger.info(f'error during sending message to user: {e}')




@router.message(F.voice | F.video_note)
async def handle_video_note(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    file_obj = message.voice or message.video_note
    time_voice_message = file_obj.duration



    # --- проерка на то что может обработать и все ок ---
    if await usp(message):
        return

    if not await if_can_process(user_id, message):
        return

    if time_voice_message > 900:
        await to_long(message)
        return



    # --- если return не вызывался то тогда обрабатываем ---


    await message.react([ReactionTypeEmoji(emoji='❤️')])
    await send(message, 'recognising')


    ext = 'ogg' if message.voice else 'mp4'
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    path = str(TEMP_DIR / f"{message.from_user.id}_{message.message_id}.{ext}")
    file_info = await bot.get_file(file_obj.file_id)
    logger.info(path)


    await bot.download_file(str(file_info.file_path), destination=path)
    await bot.send_chat_action(chat_id=message.chat.id, action='typing')




    try:
        result = await recognize(path)
        logger.info(result)


        await message.reply(
            f'<blockquote>{html.escape(result)}</blockquote>'
            f'\n\n<a href="https://github.com/platilich/anya-voice-to-text"><b>GitHub</b></a>',
            disable_web_page_preview=True,
            parse_mode='HTML'
        )



        await increase_used(user_id, time_voice_message)
        await TelegramUser.increase_count_recognise(user_id)



    except AllGroqKeysFailedError as e:
        # if no groq api keys
        logger.critical(f"CRITICAL: Groq API keys failed! {e}")

        # send message to admin
        admin_id = os.getenv("ADMIN_ID")

        text = await get_text(model='ErrorMessages', key='admin_no_groq_keys')


        if admin_id:
            try:
                await bot.send_message(
                    chat_id=int(admin_id),
                    text=text,
                    parse_mode="HTML",
                )

            except Exception as admin_err:
                logger.error(f"Failed to notify admin: {admin_err}")




        await message.react([ReactionTypeEmoji(emoji="😢")])
        await send(message, "oops")


        text = await get_text('ErrorMessages', 'service_unavailable')
        await message.answer(text)



    except Exception as e:
        # other errors

        logger.critical(f"Error during video/voice processing: {e}")

        await message.react([ReactionTypeEmoji(emoji="😢")])
        await send(message, "oops")

        text = await get_text('ErrorMessages', 'service_unavailable')
        await message.answer(text)


    finally:
        remove_temp_files([path])