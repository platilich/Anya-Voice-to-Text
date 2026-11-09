from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CopyTextButton
from bot_messages.models import Buttons
from bot_messages.models import get_text



# --- creating keyboard ---
async def keyboard_summarize():
    button_name = await get_text(model=Buttons, key='button_summarize_title')

    summarize = InlineKeyboardButton(text=str(button_name), callback_data="summarize")


    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [summarize],
        ]
    )

    print(keyboard)


    return keyboard




async def keyboard_copy(data):
    button_name = await get_text(model=Buttons, key='button_copy_title')

    copy = InlineKeyboardButton(text=str(button_name), copy_text=CopyTextButton(text=data))

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [copy],
        ]
    )


    return keyboard




async def keyboard_terms():
    button_pay_title = await get_text(model=Buttons, key='button_gift_one_star')


    pay = InlineKeyboardButton(text=str(button_pay_title), pay=True)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [pay],
        ]
    )


    return keyboard