"""from aiogram import F, types, Bot, Router
from aiogram.types import FSInputFile, ReactionTypeEmoji
from datetime import datetime, timezone
import html


from bot.utils.block_spam import usp
from bot.utils.cleanup import remove_temp_files
from bot import logger


from users.models import Limits, SubscribePlus, CustomizeMessages, TelegramUser




router = Router(name='handler_video')


@router.message(F.video | (F.document.mime_type.startswith("video/")))
async def handle_video(message: types.Message, bot: Bot):
    user_id = message.from_user.id

    if await usp(message):
        return


    processed_per_hour = await Limits.get_processed_per_hour(user_id)
    reset_time = await Limits.get_reset_time(user_id)
    current_time = datetime.now(timezone.utc)


    if processed_per_hour < 10 and reset_time is None or reset_time == current_time:

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



    else:
        if reset_time is None:
            await Limits.set_reset_time(user_id)

        await Limits.reset_processed_per_hour(user_id)


        reset_time = await Limits.get_reset_time(user_id)


        await message.answer(
            text=f'Limit 10/10 processing\nLimits will be reset at {reset_time}',
            parse_mode='HTML'
        )
"""