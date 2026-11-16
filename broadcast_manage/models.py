from django.db import models
from solo.models import SingletonModel
from datetime import datetime, time, timezone



# Create your models here.
class BroadcastTime(SingletonModel):
    def_time = datetime.combine(datetime.now(timezone.utc).date(), time(9), tzinfo=timezone.utc)
    scheduled_at = models.TimeField(default=def_time, verbose_name='Applies only after restart')


    class Meta:
        verbose_name = 'Broadcast scheduled'
        verbose_name_plural = 'Broadcast scheduled'



    def __str__(self):
        return 'Broadcast scheduled'



async def get_time_broadcast():
    # --- getting a new value from the database ---
    result, created = await BroadcastTime.objects.aget_or_create()


    return result.scheduled_at






class BroadcastTexts(SingletonModel):
    text = models.TextField(
        default='Hi, I added 3 minutes to you, have a nice day!',
        verbose_name='Daily 3 minutes added'

    )

    class Meta:
        verbose_name = 'Broadcast text message'
        verbose_name_plural = 'Broadcast text message'


    def __str__(self):
        return 'Broadcast text message'


async def get_broadcast_text():
    # --- getting a new value from the database ---
    result, created = await BroadcastTexts.objects.aget_or_create()

    return result.text





class BroadcastStatus(SingletonModel):
    broadcast_turn_off = models.BooleanField(
        default=False,
        verbose_name='Turn off broadcast'
    )

    class Meta:
        verbose_name = 'Broadcast status'
        verbose_name_plural = 'Broadcast status'


    def __str__(self):
        return 'Broadcast status'


async def broadcast_not_work():
    # --- getting a new value from the database ---
    result, created = await BroadcastStatus.objects.aget_or_create()

    return result.broadcast_turn_off