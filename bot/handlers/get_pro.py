from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import FSInputFile


from bot.middlewares.filters import check_user, is_work_command
from bot.utils.sticker import send
from bot.logger import logger
from bot.keyboards.create_keyboard import keyboard_terms


from bot_messages.models import SubscriptionPlusMessages, ErrorMessages
from bot_messages.models import get_text
from users.models import SubscribePlus
from core.models import get_price_subscription

import html


from pathlib import Path



router = Router(name='command_get_pro')



@router.message(Command("get_pro"))
async def cmd_get_pro(message: types.Message):
    logger.info('command /get_pro')
    if await is_work_command():
        logger.info('not work')
        return


    if await check_user(message=message):
        return


    logger.info(f'send invoice pro | {message.from_user.id}')



    # --- getting texts from models ---
    text_title = await get_text(model=SubscriptionPlusMessages, key='invoice_title')
    text_description = await get_text(model=SubscriptionPlusMessages, key='invoice_description')


    # --- getting the current subscription price ---
    current_price = await get_price_subscription()
    prices = [types.LabeledPrice(label=text_title, amount=current_price)]




    # --- sending a photo ---
    project_root = Path(__file__).resolve().parent.parent
    screen_file = project_root / "screens" / "get_pro.jpg"
    photo = FSInputFile(screen_file)

    await message.answer_photo(photo=photo)



    # --- sending a invoice ---
    keyboard = await keyboard_terms('https://telegra.ph/Terms-of-Service--Refund-Policy-10-17')

    await message.answer_invoice(
        title=f"Project Support ({current_price} Stars)",
        description=text_description,
        payload=f"premium_donation_{current_price}_stars",
        provider_token="",
        currency="XTR",
        prices=prices,
        start_parameter="get-premium",
        reply_markup=keyboard,
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