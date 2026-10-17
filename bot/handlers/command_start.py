from aiogram import Router, types
from aiogram.filters import Command
from bot.utils.block_spam import usp
import html


router = Router(name='command_start')


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    if await usp(message): # update, save, protect
        return



    sticker_file_id = 'CAACAgIAAxkBAAIBtWrTv6W42k8UUnhLJcVJaz9aV8JQAALttQAC4jSgSrBHFFLQInDGPQQ'
    await message.answer_sticker(sticker=sticker_file_id)


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