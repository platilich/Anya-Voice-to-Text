from aiogram import Router, F, types
from aiogram.filters import Command


from bot.middlewares.filters import check_user
from bot.utils.sticker import send
from bot.logger import logger


from bot_messages.models import SubscriptionPlusMessages, ErrorMessages
from bot_messages.models import get_text
from users.models import SubscribePlus
from core.models import get_price_subscription

import html



router = Router(name='command_get_plus')



@router.message(Command("get_plus"))
async def cmd_get_plus(message: types.Message):
    if await check_user(message=message):
        return


    logger.info('got command /get_plus')

    # --- sending a sticker ---
    await send(message, name_sticker='plus')


    # --- getting texts from models ---
    text_title = await get_text(model=SubscriptionPlusMessages, key='invoice_title')
    text_description = await get_text(model=SubscriptionPlusMessages, key='invoice_description')

    # --- getting the current subscription price ---
    current_price = await get_price_subscription()


    prices = [types.LabeledPrice(label=text_title, amount=current_price)]


    logger.info(f'send invoice plus | {message.from_user.id}')

    await message.answer_invoice(
        title=f"Project Support ({current_price} Stars)",
        description=text_description,
        payload=f"premium_donation_{current_price}_stars",
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

    logger.info('confirming the transaction')



# --- successful payment handler ---
@router.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    payment_info = message.successful_payment



    price_now = await get_price_subscription() # --- current price ---
    paid = int(payment_info.total_amount)


    expected_payload = f"premium_donation_{price_now}_stars"

    if payment_info.invoice_payload != expected_payload or paid != price_now or payment_info.currency != 'XTR':
        logger.info(f"Something is wrong with the user's payment.: {user_id}. We are got from user: {paid}, Currency: {payment_info.currency}")


        # --- if something don't correct ---
        try:
            logger.info('we write to the user that something is wrong with the payment.')

            failed_payment = await get_text(model=SubscriptionPlusMessages, key='failed_payment')
            await message.answer(failed_payment)

        except Exception as e:
            logger.error(f"couldn't send message to user: {user_id}\nerror: {e}")


        try:
            logger.info(f'refund money to user: {user_id}')
            await message.bot.refund_payment(
                user_id=user_id,
                telegram_payment_charge_id=payment_info.telegram_payment_charge_id,
            )

        except Exception as e:
            logger.error(f'error when transferring money to user: {user_id}\nerror: {e}')




        try:
            logger.info('we write to the user that something is wrong with the payment.')

            text = await get_text(model=ErrorMessages, key='refund_payment')
            await message.answer(text)

        except Exception as e:
            logger.error(f"couldn't send message to user: {user_id}\nerror: {e}")



        logger.info('We are refund the money')

        return



    # --- sending thanks for the purchase ---
    try:
        text = await get_text(model=SubscriptionPlusMessages, key='success_purchase')
        response = text.replace('{name}', str(html.escape(name))).replace('{payment_info.total_amount}', str(payment_info.total_amount))
        await message.answer(response)


    except Exception as e:
        logger.error(f'failed send thanks for plus: {e}')



    try:
        await send(message, 'love')
        logger.info('user bought subscribe')


    except Exception as e:
        logger.info(f'failed send sticker love: {e}')



    await SubscribePlus.give_subscribe(user_id)

    logger.info('give user subscribe')