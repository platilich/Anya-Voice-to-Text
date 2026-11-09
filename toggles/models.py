from django.db import models
from solo.models import SingletonModel
from cachetools import TTLCache



cache_summarize_button = TTLCache(maxsize=1, ttl=180)
cache_status_command = TTLCache(maxsize=1, ttl=180)


# Create your models here.
class CommandGetProStatus(SingletonModel):
    turn_off_get_pro = models.BooleanField(
        default=False,
        verbose_name='Turn off /get_pro command'
    )


    class Meta:
        verbose_name = 'Payment for Pro subscription'
        verbose_name_plural = 'Payment for Pro subscription'



    def __str__(self):
        return 'Command /get_pro status'


    @classmethod
    async def get_status_command_get_pro(cls):
        if "command_status" in cache_status_command:
            return cache_status_command['command_status']


        result = await cls.objects.aget()
        cache_status_command['command_status'] = result.turn_off_get_pro

        return result.turn_off_get_pro



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
        if "button_status" in cache_summarize_button:
            return cache_summarize_button["button_status"]


        # --- getting a new value from the database ---
        result = await cls.objects.aget()

        # --- cached to reduce database load ---
        cache_summarize_button["button_status"] = result.turn_off_btn

        return result.turn_off_btn