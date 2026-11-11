from aiogram import Router, F, Bot, types
from aiogram.types import ReactionTypeEmoji
import asyncio
import html
from collections import defaultdict

from bot.utils.cleanup import remove_temp_files
from bot.services.recognition import recognize, AllGroqKeysFailedError
from bot.keyboards.create_keyboard import keyboard_summarize
from bot.logger import logger
from bot.utils.download import download_file, failed_message, notify_admin
from bot.middlewares.filters import check_user
from bot.middlewares.permission_recognize import not_enough_minutes

from users.models import TelegramUser
from toggles.models import SummarizeButtonSettings



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
        if await not_enough_minutes(message, user_id, duration_voice_message):
            return


        # --- sending reaction ---
        await message.react([ReactionTypeEmoji(emoji='❤️')])
        await bot.send_chat_action(chat_id=message.chat.id, action='typing')


        path = None



        try:
            # --- increasing the time used for the limits ---
            await TelegramUser.spend_seconds(user_id, duration_voice_message)


            # --- download the file ---
            path = await download_file(bot, message, file_obj)

            # --- calling the function to recognize audio. path to function recognize: bot/utils/audio_recogniation.py
            result = await recognize(path)
            logger.info(f'recognised: {result}')

            count_words = len(result.split())


            is_turn_off = await SummarizeButtonSettings.get_status_btn_summarize()

            if count_words > 50 and not is_turn_off:
                keyboard = await keyboard_summarize()


                await message.reply(
                    text=f'<blockquote>{html.escape(result)}</blockquote>',
                    disable_web_page_preview=True,
                    parse_mode='HTML',
                    reply_markup=keyboard
                )



            else:
                await message.reply(
                    text=f'<blockquote>{html.escape(result)}</blockquote>',
                    disable_web_page_preview=True,
                    parse_mode='HTML'
                )




            # --- increase statistic ---
            await TelegramUser.increase_count_recognise(user_id)



        except AllGroqKeysFailedError as e:
            logger.critical(f'groq keys failed: {e}')

            # --- calling the function to inform the admin about problems with Groq API keys ---
            await notify_admin(bot)

            # --- reduce used seconds ---
            await TelegramUser.add_seconds(user_id, duration_voice_message)

            await failed_message(message)



        except Exception as e:
            logger.critical(f'failed process voice: {e}')

            # --- reduce used seconds ---
            await TelegramUser.add_seconds(user_id, duration_voice_message)


            await failed_message(message)


        finally:
            if path:
                remove_temp_files([path])