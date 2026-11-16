from django.db import models
from solo.models import SingletonModel
from cachetools import TTLCache


cache = TTLCache(maxsize=4, ttl=180)



# Create your models here.
class CountMinutes(SingletonModel):
    count_minutes_new_user = models.IntegerField(default=180, verbose_name="Number of minutes - reward for clicking on a friend's link")
    count_minutes_for_owner_link = models.IntegerField(default=360, verbose_name=f'Number of minutes - reward for inviting a friend')



    def __str__(self):
        return 'Reward for new user and inviter'



    class Meta:
        verbose_name = 'Reward for new user and inviter'
        verbose_name_plural = 'Reward for new user and inviter'




async def get_count_minutes(key):
    if key in cache:
        return cache[key]

    result, created = await CountMinutes.objects.aget_or_create()

    cache[key] = int(getattr(result, key))

    return int(cache[key])




class TextsReferenceLinks(SingletonModel):
    # --- for new user ---
    ref_link_success_new_user = models.TextField(
        max_length=255,
        default='✨ Enjoy 3 free minutes-you’re here thanks to a friend! ✨',
        verbose_name='Refund confirmation'

    )

    # --- for owner link ---
    ref_link_success_owner = models.TextField(
        max_length=255,
        default='✨ Your friend, {name}, followed the link! You both get 3 minutes! ✨',
        verbose_name='Refund confirmation'

    )




    def __str__(self):
        return 'Setting reference links'




    class Meta:
        verbose_name = 'Setting reference links'
        verbose_name_plural = 'Setting reference links'




async def get_texts_for_reference(key):
    if key in cache:
        return cache[key]

    result, created = await TextsReferenceLinks.objects.aget_or_create()


    cache[key] = getattr(result, key)

    return cache[key]