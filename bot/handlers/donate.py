from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import FSInputFile, LabeledPrice


from bot.keyboards.create_keyboard import keyboard_donate
from bot.logger import logger
from bot_messages.models import get_text, DonateMessages


from core.models import DonatePrice
from pathlib import Path
import html


router = Router(name="command_donate")


DONATION_PAYLOAD = "donate_1_star"



@router.message(Command("donate"))
async def command_donate(message: types.Message):
    logger.info("command /donate")

    keyboard = await keyboard_donate()


    invoice_title = await get_text(DonateMessages, key='invoice_title')
    invoice_description = await get_text(DonateMessages, key='invoice_description')


    amount = await DonatePrice.get_donate_price()

    project_root = Path(__file__).resolve().parent.parent
    screen_file = project_root / "screens" / "donate.jpeg"
    photo = FSInputFile(screen_file)



    await message.answer_photo(
        photo=photo,
        parse_mode='HTML',
        disable_web_page_preview=True
    )


    await message.answer_invoice(
        title=invoice_title,
        description=invoice_description,
        payload=DONATION_PAYLOAD,
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="Donate", amount=amount)],
        start_parameter="donate",
        reply_markup=keyboard,
    )



@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)




@router.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    name = message.from_user.first_name


    text = await get_text(DonateMessages, key='success_donate')

    response = text.replace('{name}', html.escape(name))


    project_root = Path(__file__).resolve().parent.parent
    screen_file = project_root / "screens" / "success_donate.jpg"
    photo = FSInputFile(screen_file)



    await message.answer_photo(
        photo=photo,
        caption=response,
        parse_mode='HTML',
        disable_web_page_preview=True
    )