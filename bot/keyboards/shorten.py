from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot_messages.models import ButtonSummarize
from bot_messages.models import get_text



# --- creating keyboard ---
async def keyboard_summarize():
    button_name = await get_text(model=ButtonSummarize, key='button_title')
    summarize = InlineKeyboardButton(text=str(button_name), callback_data="summarize")

    keyboard_shorten = InlineKeyboardMarkup(
        inline_keyboard=[
            [summarize],
        ]
    )

    return keyboard_shorten