from django.db import models
from django.db.models import F
from datetime import datetime, timezone, timedelta


# Create your models here.
class TelegramUser(models.Model):
    user_id = models.BigIntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=255, blank=True, verbose_name='Name')
    nickname = models.CharField(max_length=255, blank=True, null=True, verbose_name='Nickname')
    count_recognise = models.PositiveIntegerField(default=0, verbose_name='Number of recognise voice messages into text')
    seconds_balance = models.IntegerField(default=120, verbose_name='Seconds balance')
    balance_free_added = models.DateTimeField(null=True, verbose_name='Balance ended')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Registered')
    is_banned = models.BooleanField(default=False, verbose_name='Banned')


    class Meta:
        verbose_name_plural = "Telegram users"



    @classmethod
    async def save_or_update_user(cls, user_id: int, name: str, nickname: str):
        user, created = await TelegramUser.objects.aupdate_or_create(
            user_id=user_id,
            defaults={
                'name': name,
                'nickname': nickname
            }
        )


        return user, created



    @classmethod
    async def increase_count_recognise(cls, user_id: int):
        await TelegramUser.objects.filter(user_id=user_id).aupdate(count_recognise=F('count_recognise') + 1)


    @classmethod
    async def change_status_banned(cls, user_id: int, is_banned: bool):
        await TelegramUser.objects.filter(user_id=user_id).aupdate(is_banned=is_banned)


    @classmethod
    async def get_statistic(cls, user_id: int):
        user_data = await TelegramUser.objects.filter(user_id=user_id).aget()

        return user_data.count_recognise





    @classmethod
    async def add_seconds(cls, user_id: int, seconds: int):
        await TelegramUser.objects.filter(user_id=user_id).aupdate(seconds_balance=F('seconds_balance') + seconds)


    @classmethod
    async def spend_seconds(cls, user_id: int, seconds: int):
        await TelegramUser.objects.filter(user_id=user_id).aupdate(seconds_balance=F('seconds_balance') - seconds)



    @classmethod
    async def check_can_we_add_daily_free_seconds(cls, user_id: int):
        user = await TelegramUser.objects.filter(user_id=user_id).aget()
        now = datetime.now(timezone.utc)

        if user.balance_free_added is None or user.balance_free_added <= now:
            await cls.add_seconds(user_id, seconds=180)
            await TelegramUser.objects.filter(user_id=user_id).aupdate(
                balance_free_added=now + timedelta(days=1)
            )



    @classmethod
    async def not_enough_seconds(cls, user_id: int, seconds: int):
        data = await TelegramUser.objects.filter(user_id=user_id).aget()

        if data.seconds_balance - seconds > 0:
            return False


        return True


    @classmethod
    async def get_usage_for_profile(cls, user_id: int): # --- for profile, formatted time ---
        left_seconds = await TelegramUser.objects.filter(user_id=user_id).aget()


        return left_seconds.seconds_balance


    @classmethod
    async def banned_user(cls, user_id: int):
        try:
            user = await TelegramUser.objects.filter(user_id=user_id).aget()

        except TelegramUser.DoesNotExist:
            return False

        return user.is_banned



    def __str__(self):
        return f"{self.name} ({self.user_id})"




class ReferenceLinks(models.Model):
    user_id = models.OneToOneField(TelegramUser, on_delete=models.CASCADE, primary_key=True)
    count_invited = models.IntegerField(default=0)



    @classmethod
    async def create_new_link(cls, user_id: int):
        user = await TelegramUser.objects.aget(pk=user_id)

        obj, created = await cls.objects.aget_or_create(
            user_id=user
        )
        return obj



    @classmethod
    async def increase_invited_users(cls, user_id: int, from_user_id: int):
        if user_id == from_user_id:
            return

        await ReferenceLinks.objects.filter(user_id=from_user_id).aupdate(count_invited=F('count_invited') + 1)



    class Meta:
        verbose_name = 'Reference Link'
        verbose_name_plural = 'Reference Links'


    def __str__(self):
        return f'{self.user_id} invited: {self.count_invited} user(s)'