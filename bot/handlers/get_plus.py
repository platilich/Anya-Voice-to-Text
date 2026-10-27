from aiogram import Router, F, types
from aiogram.filters import Command


# --- bot/ ---
from bot.middlewares.block_spam import usp
from bot.utils.sticker import send
from bot.logger import logger


# --- models ---
from bot_messages.models import SubscriptionPlusMessages
from bot_messages.models import get_text
from users.models import SubscribePlus


# --- insert the name safety ---
import html



router = Router(name='command_get_plus')



@router.message(Command("get_plus"))
async def cmd_get_plus(message: types.Message):
    if await usp(message):
        return


    # --- sending a sticker ---
    await send(message, name_sticker='plus')



    # --- getting texts from models ---
    text_title = await get_text(model=SubscriptionPlusMessages, key='invoice_title')
    text_description = await get_text(model=SubscriptionPlusMessages, key='invoice_description')




    prices = [types.LabeledPrice(label=text_title, amount=5)]

    # --- sending an invoice to telegram stars ---
    await message.answer_invoice(
        title="Project Support (5 Stars)",
        description=text_description,
        payload="premium_donation_5_stars",
        provider_token="",
        currency="XTR",
        prices=prices,
        start_parameter="get-premium"
    )



# --- PreCheckoutQuery ---
@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
    # --- confirming the transaction ---
    await pre_checkout_query.answer(ok=True)


# --- successful payment handler ---
@router.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    payment_info = message.successful_payment

    # --- if the payment was successful ---
    if payment_info.invoice_payload == "premium_donation_5_stars":
        try:
            await send(message, 'love')


        except Exception as e:
            logger.info(f"The field with the sticker didn't seem to be filled in or there is no such ID.: {e}")


        # --- we are issuing a subscription ---
        await SubscribePlus.give_subscribe(user_id)


        # --- sending thanks for the purchase ---
        text = await get_text(model=SubscriptionPlusMessages, key='success_purchase')
        response = text.replace('{name}', html.escape(name)).replace('{payment_info.total_amount}', payment_info.total_amount)
        await message.answer(response)