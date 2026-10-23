import html

from aiogram import Router, F, types
from aiogram.filters import Command
from bot.utils.block_spam import usp

from users.models import SubscribePlus
from bot.sticker import send
from bot.logger import logger


from bot_messages.models import get_text


router = Router(name='command_get_plus')



@router.message(Command("get_plus"))
async def cmd_get_plus(message: types.Message):
    if await usp(message):  # update, save, protect
        return



    await send(message, 'plus')




    text_title = await get_text('SubscriptionPlusMessages', 'invoice_title')
    text_description = await get_text('SubscriptionPlusMessages', 'invoice_description')




    prices = [types.LabeledPrice(label=text_title, amount=50)]


    # Отправка счета в Telegram Stars
    await message.answer_invoice(
        title="Project Support (50 Stars)",
        description=text_description,

        payload="premium_donation_50_stars",  # Уникальный ID платежа
        provider_token="",                    # Для Telegram Stars ОСТАВЛЯЕМ ПУСТЫМ!
        currency="XTR",                       # Код валюты Telegram Stars
        prices=prices,
        start_parameter="get-premium"
    )



# 1. ОБРАБОТЧИК ПРЕДВАРИТЕЛЬНОЙ ПРОВЕРКИ (PreCheckoutQuery)
# Обязателен для Telegram, чтобы подтвердить возможность списения звезд.
@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
    # Подтверждаем транзакцию
    await pre_checkout_query.answer(ok=True)


# 2. ОБРАБОТЧИК УСПЕШНОЙ ОПЛАТЫ
@router.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    payment_info = message.successful_payment

    if payment_info.invoice_payload == "premium_donation_50_stars":
        try:
            await send(message, 'love')


        except Exception as e:
            logger.info(f"The field with the sticker didn't seem to be filled in or there is no such ID.: {e}")


        await SubscribePlus.give_subscribe(user_id)

        text = await get_text('SubscriptionPlusMessages', 'success_purchase')

        response = text.replace('{name}', html.escape(name)).replace('{payment_info.total_amount}', payment_info.total_amount)

        await message.answer(response)