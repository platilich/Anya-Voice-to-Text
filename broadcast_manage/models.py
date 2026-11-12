from django.db import models
from solo.models import SingletonModel
from datetime import datetime, time, timezone



# Create your models here.
def default_time():
    return datetime.combine(
        datetime.now(timezone.utc).date(),
        time(9),
        tzinfo=timezone.utc)



class BroadcastTime(SingletonModel):
    def_time = default_time()

    scheduled_at = models.TimeField(
        default=def_time,


    verbose_name='Applies only after restart'
    )



    class Meta:
        verbose_name = 'Broadcast scheduled'
        verbose_name_plural = 'Broadcast scheduled'


    def __str__(self):
        return 'Broadcast scheduled'



    @classmethod
    async def get_time_broadcast(cls):
        # --- getting a new value from the database ---
        result, created = await cls.objects.aget_or_create(
            defaults={'scheduled_at': False}
        )


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



    @classmethod
    async def get_broadcast_text(cls):
        # --- getting a new value from the database ---
        def_time = default_time()
        result, created = await cls.objects.aget_or_create(
            defaults={'text': def_time}
        )

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



    @classmethod
    async def broadcast_not_work(cls):
        # --- getting a new value from the database ---
        result, created = await cls.objects.aget_or_create(
            defaults={'broadcast_turn_off': False}
        )

        return result.broadcast_turn_off