from aiogram import Router, F, Bot, types
from aiogram.types import ReactionTypeEmoji

# --- for a safe name stand ---
import html


# --- models ---
from users.models import TelegramUser


# --- bot/utils/ ----
from bot.middlewares.limits import increase_used
from bot.middlewares.block_spam import usp_on_voice
from bot.utils.cleanup import remove_temp_files
from bot.services.recognition import recognize, AllGroqKeysFailedError


# -- keyboards ---
from bot.keyboards.shorten import keyboard_summarize

# --- functions bot/ ---
from bot.logger import logger
from bot.utils.sticker import send
from bot.utils.download import download_file, failed_message, notify_admin




router = Router(name='handler_video')





@router.message(F.voice | F.video_note)
async def handle_video_note(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    file_obj = message.voice or message.video_note
    time_voice_message = file_obj.duration


    # --- verification: can we process the voice message ---
    if await usp_on_voice(message, time_voice_message):
        return


    # --- increasing the time used for the limits ---
    await increase_used(user_id, time_voice_message)


    # --- sending reaction ---
    await message.react([ReactionTypeEmoji(emoji='❤️')])
    await send(message, 'recognising')
    await bot.send_chat_action(chat_id=message.chat.id, action='typing')



    # --- attempt to recognize a voice message ---
    path = None

    try:
        # --- download the file ---
        path = await download_file(bot, message, file_obj)

        # --- calling the function to recognize audio. path to function recognize: bot/utils/audio_recogniation.py
        result = await recognize(path)
        logger.info(result)

        count_words = len(result.split())


        if count_words < 50:
            # --- send result to user without button (summarize) ---
            await message.reply(
                f'<blockquote>{html.escape(result)}</blockquote>'
                f'\n\n<a href="https://github.com/platilich/anya-voice-to-text"><b>GitHub</b></a>',
                disable_web_page_preview=True,
                parse_mode='HTML'
            )


        else:
            keyboard = await keyboard_summarize()
            # --- send result to user with button ---
            await message.reply(
                f'<blockquote>{html.escape(result)}</blockquote>'
                f'\n\n<a href="https://github.com/platilich/anya-voice-to-text"><b>GitHub</b></a>',
                disable_web_page_preview=True,
                parse_mode='HTML',
                reply_markup=keyboard
            )


        # --- increase statistic ---
        await TelegramUser.increase_count_recognise(user_id)




    # --- problem with Groq keys ---
    except AllGroqKeysFailedError as e:
        # if no groq api keys
        logger.critical(f"CRITICAL: Groq API keys failed! {e}")


        # --- calling the function to inform the admin about problems with Groq API keys ---
        await notify_admin(bot)


        # --- calling the function to inform the user about the error ---
        await failed_message(message)



    # --- other errors ---
    except Exception as e:
        logger.critical(f"Error during video/voice processing: {e}")


        # --- calling the function to inform the user about the error ---
        await failed_message(message)


    # --- remove temp files ---
    finally:
        if path:
            remove_temp_files([path])