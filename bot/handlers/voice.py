from importlib.resources import path

from aiogram import Router, F, Bot, types
from aiogram.types import ReactionTypeEmoji, FSInputFile
import asyncio
import html

from bot.utils.download import download_file
from bot.services.recognition import recognize
from bot.keyboards.create_keyboard import keyboard_summarize
from bot.utils.cleanup import remove_temp_files
from bot.logger import logger

from bot.middlewares.filters import check_user
from bot.middlewares.permission_recognize import not_enough_minutes


from messages.rejection_messages import (failed_downloaded_file,
                                         failed_message,
                                         gemini_limits,
                                         send_message_little_longer,
                                         notify_admin
                                    )

from users.models import TelegramUser
from collections import defaultdict





router = Router(name='handler_video')


user_locks = defaultdict(asyncio.Lock)



async def get_user_lock(user_id: int) -> asyncio.Lock:
    if user_id not in user_locks:
        user_locks[user_id] = asyncio.Lock() # --- add user into the list ---

    return user_locks[user_id]





async def send_start_recognise(message, path):
    for i in range(3):
        result = await recognize(path)

        code = result[0]
        status = result[1]


        if status is not False:
            return result[0]


        if code == 429:
            logger.warning("The limits on our Gemini AI API account have ended")
            await gemini_limits(message)
            break


        if code in (500, 503, 504):
            logger.warning(f"Временная ошибка сервиса: {code}")

            if i == 0:
                await send_message_little_longer(message)


            if i == 2:
                await failed_message(message)
                await notify_admin(message)

                break




        await asyncio.sleep(10)





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
            if await not_enough_minutes(message, duration_voice_message):
                return


            # --- sending reaction ---
            await message.react([ReactionTypeEmoji(emoji='❤️')])
            await bot.send_chat_action(chat_id=message.chat.id, action='typing')



            # --- increasing the time used for the limits ---
            await TelegramUser.spend_seconds(user_id, duration_voice_message)



            path = None

            # --- download the file ---
            try:
                path = await download_file(bot, message, file_obj)

            except:
                pass

            if path is None:
                try:
                    await failed_downloaded_file(message)

                except Exception as e:
                    logger.error(f'failed to reply to user: {e}')

                return


            # --- calling the function to recognize audio. path to function recognize: bot/utils/audio_recogniation.py

            result = str(await send_start_recognise(message, path))


            if result:
                logger.info(f'recognised: {result}')



                count_words = len(result.split())




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