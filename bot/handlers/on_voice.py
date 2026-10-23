from aiogram import Router, F, Bot, types
from aiogram.types import ReactionTypeEmoji

import html
import os
from pathlib import Path


from users.models import TelegramUser


from bot.utils.limits import if_process_limit_allowed, increase_processed
from bot.utils.block_spam import usp
from bot.utils.cleanup import remove_temp_files
from bot.utils.audio_recognation import recognize, AllGroqKeysFailedError
from bot.logger import logger
from dotenv import load_dotenv


from bot.sticker import send
from bot_messages.models import get_text


load_dotenv()


# bot/handlers/this_file.py -> корень проекта, не зависит от cwd
TEMP_DIR = Path(__file__).resolve().parents[2] / "temp"


router = Router(name='handler_video')




@router.message(F.voice | F.video_note)
async def handle_video_note(message: types.Message, bot: Bot):
    user_id = message.from_user.id

    if await usp(message):
        return


    if await if_process_limit_allowed(user_id, message):
        await message.react([ReactionTypeEmoji(emoji='❤️')])
        await send(message, 'recognising')



        ext = 'ogg' if message.voice else 'mp4'
        file_obj = message.voice or message.video_note
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


            await increase_processed(user_id)
            await TelegramUser.increase_count_recognise(user_id)


        except AllGroqKeysFailedError as e:
            # обработка ошибок от groq api keys
            logger.critical(f"CRITICAL: Groq API keys failed! {e}")

            # Отправка уведомления админу
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


            text = await get_text('something_went_wrong')
            await message.answer(text)



        except Exception as e:
            # обработка любых других рандомных ошибок
            logger.critical(f"Error during video/voice processing: {e}")

            await message.react([ReactionTypeEmoji(emoji="😢")])
            await send(message, "oops")


            text = await get_text('something_went_wrong')
            await message.answer(text)



        finally:
            # удаляем временный файл в любом случае
            remove_temp_files([path])