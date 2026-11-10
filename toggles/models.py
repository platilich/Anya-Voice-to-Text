from django.db import models
from solo.models import SingletonModel
from cachetools import TTLCache



cache_summarize_button = TTLCache(maxsize=1, ttl=180)
cache_status_command = TTLCache(maxsize=1, ttl=180)


# Create your models here.
class ShopStatus(SingletonModel):
    turn_off_shop = models.BooleanField(
        default=True,
        verbose_name='Turn off /shop command'
    )


    class Meta:
        verbose_name = 'Shop status'
        verbose_name_plural = 'Shop status'



    def __str__(self):
        return 'Command /shop'


    @classmethod
    async def get_status_shop(cls):
        if "command_status" in cache_status_command:
            return cache_status_command['command_status']


        result, created = await cls.objects.aget_or_create(
            defaults={'turn_off_shop': False}
        )

        cache_status_command['command_status'] = result.turn_off_shop
        # возращаем True допустим
        return result.turn_off_shop



class SummarizeButtonSettings(SingletonModel):
    turn_off_btn = models.BooleanField(
        default=False,
        verbose_name='Turn off summarize button'
    )


    class Meta:
        verbose_name = 'Summarize button'
        verbose_name_plural = 'Summarize button'


    def __str__(self):
        return 'Summarize button'


    @classmethod
    async def get_status_btn_summarize(cls):
        # --- if the value is in the cache, we return it ---
        if "turn_off_btn" in cache_summarize_button:
            return cache_summarize_button["turn_off_btn"]


        # --- getting a new value from the database ---
        result, created = await cls.objects.aget_or_create(
            defaults={'turn_off_btn': False}
        )

        # --- cached to reduce database load ---
        cache_summarize_button["turn_off_btn"] = result.turn_off_btn

        return result.turn_off_btn