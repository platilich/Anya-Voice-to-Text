from django.db import models
from solo.models import SingletonModel
from cachetools import TTLCache




cache_text = TTLCache(maxsize=3, ttl=180)
cache_price = TTLCache(maxsize=1, ttl=180)



# Create your models here.
class ShopTexts(SingletonModel):
    # texts for invoicing and successful payments
    invoice_title = models.TextField(
        max_length=255,
        default="Buy minute package",
        verbose_name="Invoice Title"
    )


    invoice_description = models.TextField(
        default="Buy a minute package in Ani, 3 minutes, for 7 days",
        verbose_name="Invoice Description"
    )


    success_bought = models.TextField(
        max_length=255,
        default="✨ {name}, thank you very much for your purchase! ❤️",
        verbose_name="Success Purchase Message ({name}, {payment_info.total_amount})"
    )


    failed_payment = models.TextField(
        max_length=255,
        default=(
            "⚠️ Looks like the price changed, or the payment was made in a different currency. "
            "I’ll send the money back to your account.\n\n"
            "Please get a new invoice with /get_plus."
        ),
        verbose_name='Price change or currency mismatch notice',

    )


    refund_payment = models.TextField(
        max_length=255,
        default='✅ All sorted!\nI’ve sent the money back to your account.',
        verbose_name='Refund confirmation'

    )


    def __str__(self):
        return 'Subscription Payment Texts'



    class Meta:
        verbose_name = 'Subscription Payment'
        verbose_name_plural = 'Subscription Payments'




    @classmethod
    async def get_shop_text(cls, key):
        # --- if the value is in the cache, we return it ---
        if key in cache_text:
            return cache_text[key]

        # --- getting a new value from the database ---
        result, created = await cls.objects.aget_or_create(
            pk=1,
            defaults={
                "invoice_title": "Buy minute package",
                "invoice_description": "Buy a minute package in Ani, 3 minutes, for 7 days",
                "success_bought": "✨ {name}, thank you very much for your purchase! ❤️",
            },
        )

        # --- cached to reduce database load ---
        cache_text[key] = getattr(result, key)


        return cache_text[key]







class ShopMinutePrice(SingletonModel):
    price = models.IntegerField(
        blank=True,
        default=1,
        verbose_name='Price per minute in Stars (updated within 3 minutes)'
    )


    class Meta:
        verbose_name_plural = 'Minute price per minute'


    def __str__(self):
        return 'Minute price per minute'



    @classmethod
    async def get_minute_price_per_minute(cls):
        # --- if the value is in the cache, we return it ---
        if "price" in cache_price:
            return cache_price["price"]

        # --- getting a new value from the database ---
        result, created = await cls.objects.aget_or_create(
            defaults={'price': 1}
        )

        # --- cached to reduce database load ---
        cache_price["price"] = result.price

        return result.price




class ShopStatus(SingletonModel):
    shop_turn_off = models.BooleanField(
        default=False,
        verbose_name='Turn off shop'
    )

    class Meta:
        verbose_name = 'Shop status'
        verbose_name_plural = 'Shop status'


    def __str__(self):
        return 'Shop status'



    @classmethod
    async def shop_not_work(cls):
        # --- getting a new value from the database ---
        result, created = await cls.objects.aget_or_create(
            defaults={'shop_turn_off': False}
        )

        return result.shop_turn_off