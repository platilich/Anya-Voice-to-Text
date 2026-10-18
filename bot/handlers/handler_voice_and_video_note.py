from aiogram import Router, F, Bot, types
from aiogram.types import ReactionTypeEmoji

import html
import os


from users.models import TelegramUser
from bot.utils.send_sticker import send_sticker_with_anya
from bot.utils.limits import if_process_limit_allowed, increase_processed
from bot.utils.block_spam import usp
from bot.utils.cleanup import remove_temp_files
from bot.utils.audio_recognation import recognize, AllGroqKeysFailedError
from bot.logger import logger

from dotenv import load_dotenv



load_dotenv()



router = Router(name='handler_video')




@router.message(F.voice | F.video_note)
async def handle_video_note(message: types.Message, bot: Bot):
    user_id = message.from_user.id

    if await usp(message):
        return


    if await if_process_limit_allowed(user_id, message):
        await message.react([ReactionTypeEmoji(emoji='❤️')])
        await send_sticker_with_anya(message, 'recognising')



        ext = 'ogg' if message.voice else 'mp4'
        file_obj = message.voice or message.video_note
        os.makedirs('../temp', exist_ok=True)
        path = f"temp/{message.from_user.id}_{message.message_id}.{ext}"
        file_info = await bot.get_file(file_obj.file_id)
        logger.info(path)



        recognising_sticker = await bot.download_file(str(file_info.file_path), destination=path)
        await bot.send_chat_action(chat_id=message.chat.id, action='typing')



        try:
            result = await recognize(path)
            logger.info(result)


            await message.reply(
                f'<blockquote>{html.escape(result)}</blockquote>\n\n\n<b><a href="https://github.com/platilich/NoteCircle">GitHub</a></b>',
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
            if admin_id:
                try:
                    await bot.send_message(
                        chat_id=int(admin_id),
                        text=(
                            "All Groq API keys are invalid, blocked, or have reached the limit..\n"
                            "👉 <i>Add a new key to your new Groq account or top up your account balance in the admin area!</i>"
                        ),
                        parse_mode="HTML",
                    )

                except Exception as admin_err:
                    logger.error(f"Failed to notify admin: {admin_err}")


            # Ответ пользователю с извинениями
            await message.react([ReactionTypeEmoji(emoji="😢")])
            await send_sticker_with_anya(message, "oops")

            await message.answer(
                "Sorry, the audio recognition service is currently unavailable."
                " Please try again later."
            )


        except Exception as e:
            # обработка любых других рандомных ошибок
            logger.error(f"Error during video/voice processing: {e}")
            await message.react([ReactionTypeEmoji(emoji="😢")])
            await send_sticker_with_anya(message, "oops")
            await message.answer("Something went wrong...")


        finally:
            # удаляем временный файл в любом случае
            remove_temp_files([path])