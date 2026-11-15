from aiogram import Router, F, Bot, types
from aiogram.types import ReactionTypeEmoji
import asyncio
import html
from collections import defaultdict

from bot.utils.cleanup import remove_temp_files
from bot.services.recognition import recognize
from bot.keyboards.create_keyboard import keyboard_summarize
from bot.logger import logger
from bot.utils.download import download_file, failed_message, notify_admin
from bot.middlewares.filters import check_user
from bot.middlewares.permission_recognize import not_enough_minutes
from bot.middlewares.rejection_messages import failed_downloaded_file
from aiogram.types import FSInputFile

from users.models import TelegramUser



router = Router(name='handler_video')


user_locks = defaultdict(asyncio.Lock)


async def get_user_lock(user_id: int) -> asyncio.Lock:
    if user_id not in user_locks:
        user_locks[user_id] = asyncio.Lock() # --- add user into the list ---

    return user_locks[user_id]



@router.message(F.voice | F.video_note)
async def handle_video_note(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    file_obj = message.voice or message.video_note
    duration_voice_message = file_obj.duration


    logger.info('got a audio/video_note')


    if await check_user(message=message, duration_voice_message=duration_voice_message):
        return



    # --- execution queue ---
    async with user_locks[user_id]:
        try:
            if await not_enough_minutes(message, user_id, duration_voice_message):
                return


            # --- sending reaction ---
            await message.react([ReactionTypeEmoji(emoji='❤️')])
            await bot.send_chat_action(chat_id=message.chat.id, action='typing')



            # --- increasing the time used for the limits ---
            await TelegramUser.spend_seconds(user_id, duration_voice_message)


            # --- download the file ---
            path = await download_file(bot, message, file_obj)


            if path is None:
                try:
                    await failed_downloaded_file(message)

                except Exception as e:
                    logger.error(f'failed to reply to user: {e}')

                return


            # --- calling the function to recognize audio. path to function recognize: bot/utils/audio_recogniation.py
            print(path)
            result = await recognize(path)

            logger.info(f'recognised: {result}')



            count_words = len(result)




            # --- increase statistic ---
            await TelegramUser.increase_count_recognise(user_id)


            if count_words > 4096:
                with open('anya-voice-to-text', 'w+') as file:
                    file.write(result)
                    file.close()


                # --- create a file object ---
                file_to_send = FSInputFile(path="anya-voice-to-text")

                await bot.send_document(chat_id=message.chat.id, document=file_to_send)

                return



            if count_words > 50:
                keyboard = await keyboard_summarize()

                await message.reply(
                    text=f'<blockquote>{html.escape(result)}</blockquote>',
                    disable_web_page_preview=True,
                    parse_mode='HTML',
                    reply_markup=keyboard
                )

                return




            await message.reply(
                text=f'<blockquote>{html.escape(result)}</blockquote>',
                disable_web_page_preview=True,
                parse_mode='HTML'
            )



        except Exception as e:
            logger.critical(f'failed process voice: {e}')

            # --- reduce used seconds ---
            await TelegramUser.add_seconds(user_id, duration_voice_message)


            await failed_message(message)


        finally:
            if path:
                remove_temp_files([path])