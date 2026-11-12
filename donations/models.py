from django.db import models
from cachetools import TTLCache
from solo.models import SingletonModel



# Create your models here.
cache_donate = TTLCache(maxsize=1, ttl=180)
cache_text = TTLCache(maxsize=1, ttl=180)



class DonationMessages(SingletonModel):
    # texts for invoicing and successful payments
    invoice_title = models.TextField(
        max_length=255,
        default="Support the project with Anya",
        verbose_name="Invoice Title"
    )

    invoice_description = models.TextField(
        default="A small donation to support the project — 1 star.",
        verbose_name="Invoice Description"
    )

    success_donate = models.TextField(
        max_length=255,
        default=(
            "✨ {name}, thanks so much for the donation! ❤️"
        ),
        verbose_name="Success Purchase Message ({name}, {payment_info.total_amount})"
    )


    def __str__(self):
        return 'Subscription Payment Texts'



    class Meta:
        verbose_name = 'Subscription Payment'
        verbose_name_plural = 'Subscription Payments'




    @classmethod
    async def get_donate_text(cls, key):
        # --- if the value is in the cache, we return it ---
        if key in cache_text:
            return cache_text[key]

        # --- getting a new value from the database ---
        result, created = await cls.objects.aget_or_create(
            defaults={
                'invoice_title': "Support the project with Anya",
                'invoice_description': "A small donation to support the project — 1 star.",
                'success_donate': "✨ {name}, thanks so much for the donation! ❤️"
            }
        )

        # --- cached to reduce database load ---
        cache_text[key] = getattr(result, key)

        return cache_text[key]



class DonatePrice(SingletonModel):
    price = models.IntegerField(
        blank=True,
        default=1,
        verbose_name='Donate Price. (Updated within 3 minutes)'
    )


    class Meta:
        verbose_name_plural = 'Donate price'


    def __str__(self):
        return 'Donate price'



    @classmethod
    async def get_donation_price(cls):
        # --- if the value is in the cache, we return it ---
        if "price" in cache_donate:
            return cache_donate["price"]

        # --- getting a new value from the database ---
        result, created = await cls.objects.aget_or_create(
            defaults={'price': 1}
        )

        # --- cached to reduce database load ---
        cache_donate["price"] = result.price

        return result.price