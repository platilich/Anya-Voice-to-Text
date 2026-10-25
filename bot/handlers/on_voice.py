from aiogram import Router, F, Bot, types
from aiogram.types import ReactionTypeEmoji, InlineKeyboardMarkup, InlineKeyboardButton

# --- for a safe name stand ---
import html


# --- different models ---
from users.models import TelegramUser


# --- bot/utils/ ----
from bot.utils.limits import increase_used
from bot.utils.block_spam import usp_on_voice
from bot.utils.cleanup import remove_temp_files
from bot.audio.recognition import recognize, AllGroqKeysFailedError


# --- functions bot/ ---
from bot.logger import logger
from bot.sticker import send
from bot.utils.voice_helper import download_file, failed_message, notify_admin




router = Router(name='handler_video')





@router.message(F.voice | F.video_note)
async def handle_video_note(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    file_obj = message.voice or message.video_note
    time_voice_message = file_obj.duration


    # --- verification: can we process the voice message ---
    if await usp_on_voice(message, time_voice_message):
        return


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


        # --- updating the data ---
        # --- increasing the time used for the limits ---
        await increase_used(user_id, time_voice_message)


        # --- increase statistic ---
        await TelegramUser.increase_count_recognise(user_id)







        # --- creating keyboard ---
        cut_back = InlineKeyboardButton(text="Cut back", callback_data="cut_back")

        keyboard_inline = InlineKeyboardMarkup(
            inline_keyboard=[
                [cut_back],
            ]
        )


        # --- send result to user ---
        await message.reply(
            f'<blockquote>{html.escape(result)}</blockquote>'
            f'\n\n<a href="https://github.com/platilich/anya-voice-to-text"><b>GitHub</b></a>',
            disable_web_page_preview=True,
            parse_mode='HTML',
            reply_markup=keyboard_inline
        )




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