import asyncio
import os

from aiogram import Router, F, types, Bot
from aiogram.filters import Command
from aiogram.types import FSInputFile, ReactionTypeEmoji
import django
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import html

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video_note_bot.settings')
django.setup()


from .logger import logger


from .utils.cleanup import remove_temp_files
from .utils.video_note import convert_to_video_note
from .utils.audio_recognation import recognize
from .utils.block_spam import usp


from users.models import TelegramUser, CustomizeMessages




router = Router()




@router.message(Command("start"))
async def cmd_start(message: types.Message):
    if await usp(message): # update, save, protect
        return

    custom_greeting = await CustomizeMessages.get_custom_messages()

    if custom_greeting:
        await message.answer(
            text=f'{html.escape(custom_greeting)}',
            parse_mode="HTML",
            disable_web_page_preview=True
        )


        return


    message_text = (
        f"👋 Hey, <b>{html.escape(message.from_user.first_name)}</b>! ✨\n\n"
        "Here's what I can do for you:\n"
        "🎙️ Turn your voice messages into text\n"
        "🎬 Transform your videos into awesome video notes\n\n"
        "No subscriptions and no ads - just send a video and enjoy! 🚀\n\n"
        "<b>Ready to get started? Send me a video, audio, or sticker!</b> 💫\n\n"
        "<a href='https://github.com/platilich/NoteCircle'><b>GitHub</b></a>"
    )

    await message.answer(
        text=message_text,
        parse_mode="HTML",
        disable_web_page_preview=True
    )




@router.message(F.video | (F.document.mime_type.startswith("video/")))
async def handle_video(message: types.Message, bot: Bot):
    user_id = message.from_user.id

    if await usp(message):
        return


    is_document = message.document is not None
    video_data = message.document if is_document else message.video




    if not is_document and message.video.duration > 60:
        custom_limiting = await CustomizeMessages.get_custom_messages()

        if custom_limiting[2]:
            await message.answer(custom_limiting[2])
            return


        await message.answer("❌ The video is too long. The maximum length is 1 minute.")
        return


    await message.react([ReactionTypeEmoji(emoji='❤️')])


    input_file = f"downloads_{user_id}.mp4"
    output_file = f"output_{user_id}.mp4"



    try:
        file_info = await message.bot.get_file(video_data.file_id)
        await bot.download_file(str(file_info.file_path), input_file)


        success = await asyncio.to_thread(convert_to_video_note, input_file, output_file)

        if not success:
            await message.answer("Unable to process. Something went wrong.")
            logger.error(f'Something went wrong')
            return



        await bot.send_chat_action(message.chat.id, action="upload_video_note")


        video_note = FSInputFile(output_file)
        await message.answer_video_note(video_note)


        await TelegramUser.increase_count_video(user_id)



    except Exception as e:
        custom_error = await CustomizeMessages.get_custom_messages()
        if custom_error[3]:
            await message.answer(f'{html.escape(custom_error)}', parse_mode='HTML', disable_web_page_preview=True)
            return


        await message.answer("Unable to process. Something went wrong.") # error
        logger.error(f'Something went wrong {e}')



    finally:
        remove_temp_files([input_file, output_file])






@router.message(F.voice | F.video_note)
async def handle_video_note(message: types.Message, bot: Bot):
    user_id = message.from_user.id

    if await usp(message):
        return


    user = await asyncio.to_thread(TelegramUser.objects.get, user_id=user_id)

    current_time = datetime.now(ZoneInfo('UTC'))


    if not await user.can_process_voice(limit=10):
        time_left = user.voice_reset_time + timedelta(hours=1) - current_time
        minutes = int(time_left.total_seconds() / 60)
        await message.answer(f"⏳ The limit ended. Limit to update through: {minutes}")
        return




    await message.react([ReactionTypeEmoji(emoji='❤️')])


    ext = 'ogg' if message.voice else 'mp4'
    file_obj = message.voice or message.video_note

    os.makedirs('temp', exist_ok=True)

    path = f"temp/{message.from_user.id}_{message.message_id}.{ext}"

    file_info = await bot.get_file(file_obj.file_id)
    await bot.download_file(file_info.file_path, destination=path)

    await bot.send_chat_action(chat_id=message.chat.id, action='typing')

    logger.info(path)
    result = await recognize(path)

    logger.info(result)


    try:
        await message.reply(
            f'<blockquote>{html.escape(result)}</blockquote>\n\n\n<b><a href="https://github.com/platilich/NoteCircle">GitHub</a></b>',
            disable_web_page_preview=True,
            parse_mode='HTML'
        )


        await TelegramUser.increase_count_video(user_id)




    except Exception as e:
        logger.error(f'error when sending a message to the user: {e}')


    finally:
        remove_temp_files([path])