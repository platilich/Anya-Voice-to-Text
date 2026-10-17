from aiogram import Router, F, Bot, types
from aiogram.types import ReactionTypeEmoji


import html
import os


from bot.utils.limits import if_process_limit_allowed, increase_processed
from bot.utils.block_spam import usp
from bot.utils.cleanup import remove_temp_files
from bot.utils.audio_recognation import recognize
from bot.logger import logger




router = Router(name='handler_video')




@router.message(F.voice | F.video_note)
async def handle_video_note(message: types.Message, bot: Bot):
    user_id = message.from_user.id

    if await usp(message):
        return



    if await if_process_limit_allowed(user_id, message):
        await message.react([ReactionTypeEmoji(emoji='❤️')])

        sticker_file_id = 'CAACAgIAAxkBAAIBu2rTv6jBQfA-LxikLNPG8pbRcpGSAAJEtAAC4-OgSpMN2K6cuknfPQQ'
        await message.answer_sticker(sticker=sticker_file_id)

        ext = 'ogg' if message.voice else 'mp4'
        file_obj = message.voice or message.video_note

        os.makedirs('../temp', exist_ok=True)

        path = f"temp/{message.from_user.id}_{message.message_id}.{ext}"

        file_info = await bot.get_file(file_obj.file_id)
        await bot.download_file(str(file_info.file_path), destination=path)

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


            await increase_processed(user_id)



        except Exception as e:
            sticker_file_id = 'CAACAgIAAxkBAAIBv2rTv6olJPP9MtxJMTs7TqMuT7OIAAL9sAACxz6hSvltoosJC2XnPQQ'
            await message.answer_sticker(sticker=sticker_file_id)
            await message.answer('Something went wrong...')

            logger.error(f'error when sending a message to the user: {e}')


        finally:
            remove_temp_files([path])