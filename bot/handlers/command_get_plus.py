from aiogram import Router, F, types
from aiogram.filters import Command
from bot.utils.block_spam import usp
from bot.utils.send_sticker import send_sticker_with_anya
from users.models import SubscribePlus
from bot.logger import logger


router = Router(name='command_get_plus')


TERMS_URL = "https://telegra.ph/Terms-of-Service--Refund-Policy-10-17"



@router.message(Command("get_plus"))
async def cmd_get_plus(message: types.Message):
    if await usp(message):  # update, save, protect
        return



    await send_sticker_with_anya(message, 'plus')



    # Цена в Telegram Stars
    prices = [types.LabeledPrice(label="Voluntary Donation (Premium Perk)", amount=50)]

    # Отправка счета в Telegram Stars
    await message.answer_invoice(
        title="Project Support (50 Stars)",
        description="Voluntary donation to support the bot. Includes 30-day Premium perk.",
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
        # TODO: Добавьте здесь логику выдачи подписки/лимитов на 30 дней в вашей базе данных



        try:
            await send_sticker_with_anya(message, 'love')


        except Exception as e:
            logger.info(f'Поле с стикером похоже не было заполненно или такого ID нет: {e}')



        await SubscribePlus.give_subscribe(user_id)


        await message.answer(
            f"🎉 <b><i>{name}</i>, thank you for your support!</b>\n\n"
            f"Received: {payment_info.total_amount} ⭐\n"
            f"Your limit has been upgraded to up to 50 processings per hour for 1 month."
        )