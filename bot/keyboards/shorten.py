from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CopyTextButton
from bot_messages.models import Buttons
from bot_messages.models import get_text



# --- creating keyboard ---
async def keyboard_summarize():
    button_name = await get_text(model=Buttons, key='button_summarize_title')
    summarize = InlineKeyboardButton(text=str(button_name), callback_data="summarize")

    keyboard_shorten = InlineKeyboardMarkup(
        inline_keyboard=[
            [summarize],
        ]
    )

    return keyboard_shorten



async def keyboard_copy_the_link(url):
    button_name = await get_text(model=Buttons, key='button_copy_title')

    copy = InlineKeyboardButton(text=str(button_name), copy_text=CopyTextButton(text=url))

    keyboard_copy = InlineKeyboardMarkup(
        inline_keyboard=[
            [copy],
        ]
    )


    return keyboard_copy