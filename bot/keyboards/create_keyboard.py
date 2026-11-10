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




async def keyboard_donate():
    button_pay_title = await get_text(model=Buttons, key='button_gift_one_star')


    pay = InlineKeyboardButton(text=str(button_pay_title), pay=True)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [pay],
        ]
    )


    return keyboard



async def keyboard_shop():
    button_price_first = await get_text(model=Buttons, key='button_price_first')
    button_price_seconds = await get_text(model=Buttons, key='button_price_seconds')



    pay_first = InlineKeyboardButton(text=str(button_price_first), pay=True)
    pay_second = InlineKeyboardButton(text=str(button_price_seconds), pay=True)


    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [pay_first],
            [pay_second],
        ]
    )


    return keyboard