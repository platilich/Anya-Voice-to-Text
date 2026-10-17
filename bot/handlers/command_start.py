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


    name = html.escape(message.from_user.first_name or "Friend")


    message_text = (
        f"👋 Hey, <b>{name}</b>! I'm <b>Anya</b> ✨\n\n"
        "I'm here to instantly transcribe your audio & video into clear text! 🎧\n\n"
        "<b>Here is what I can do:</b>\n"
        "🎙️ Convert voice notes & audio files to text\n"
        "🎥 Transcribe Telegram video messages (circles)\n\n"
        "⚡ Fast, accurate, and super easy to use!\n\n"
        "<b>Ready to get started?</b> Just send or forward me any voice note or video message! 💫\n\n"
        "<a href='https://github.com/platilich/NoteCircle'><b>GitHub</b></a>"
    )

    await message.answer(
        text=message_text,
        parse_mode="HTML",
        disable_web_page_preview=True
    )