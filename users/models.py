from django.db import models
from django.db.models import F, DateTimeField
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta


# Create your models here.
class TelegramUser(models.Model):
    user_id = models.BigIntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=255, blank=True, verbose_name='Name')
    nickname = models.CharField(max_length=255, blank=True, null=True, verbose_name='Nickname')
    count_recognise = models.PositiveIntegerField(default=0, verbose_name='Number of processed voice messages/video notes into text')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Registered')
    is_banned = models.BooleanField(default=False, verbose_name='Banned')


    class Meta:
        verbose_name_plural = "Telegram users"



    @classmethod
    async def save_or_update_user(cls, user_id, name, nickname):
        user, created = await TelegramUser.objects.aupdate_or_create(
            user_id=user_id,
            defaults={
                'name': name,
                'nickname': nickname,
            }
        )

        return user, created



    @classmethod
    async def increase_count_recognise(cls, user_id):
        await TelegramUser.objects.filter(user_id=user_id).aupdate(count_recognise=F('count_recognise') + 1)


    @classmethod
    async def change_status_banned(cls, user_id, is_banned):
        await TelegramUser.objects.filter(user_id=user_id).aupdate(is_banned=is_banned)



    @classmethod
    async def get_statistic(cls, user_id):
        user_data = await TelegramUser.objects.filter(user_id=user_id).aget()

        return [user_data.count_recognise]




    @classmethod
    async def banned_user(cls, user_id):
        try:
            user = await TelegramUser.objects.filter(user_id=user_id).aget()
        except cls.DoesNotExist:
            return False

        return user.is_banned



    def __str__(self):
        return f"{self.name} ({self.user_id})"




class SubscribePlus(models.Model):
    user_id = models.OneToOneField(TelegramUser, on_delete=models.CASCADE, primary_key=True)
    is_plus = models.BooleanField(default=False)
    subscribe_ending = DateTimeField(null=True, blank=True)


    @classmethod
    async def get_or_create_plus(cls, user_id):
        """Вспомогательный метод: находит или автоматически создаёт юзара в таблице Subscribe Plus с отсутсвием подписки (False) и датой истечением None"""
        user_obj = await TelegramUser.objects.aget(pk=user_id)
        subscribe_obj, _ = await cls.objects.aget_or_create(
            user_id=user_obj,
            defaults={'is_plus': False, 'subscribe_ending': None}
        )
        return subscribe_obj



    @classmethod
    async def give_subscribe(cls, user_id):
        subscribe = await SubscribePlus.get_or_create_plus(user_id)

        now = datetime.now(timezone.utc)
        start = now
        # если плюс ещё действует, прибавляем месяц к концу, а не затираем его
        if subscribe.subscribe_ending and subscribe.subscribe_ending > now:
            start = subscribe.subscribe_ending

        subscribe_ending_date = start + relativedelta(months=1)
        await SubscribePlus.objects.filter(user_id=user_id).aupdate(is_plus=True, subscribe_ending=subscribe_ending_date)


    @classmethod
    async def left_days_subscribe(cls, user_id):
        await SubscribePlus.get_or_create_plus(user_id)
        user_data = await SubscribePlus.objects.aget(user_id=user_id)


        current_data = datetime.now(timezone.utc)
        ending_subscribe_date = user_data.subscribe_ending


        if ending_subscribe_date and ending_subscribe_date > current_data:
            time_left = ending_subscribe_date - current_data
            days_left = time_left.days  # полных оставшихся дней

            return days_left


        return None



    @classmethod
    async def user_message_status_subscribe(cls, user_id):
        # 0 тоже валиден: подписка кончается сегодня
        return await SubscribePlus.left_days_subscribe(user_id)






    @classmethod
    async def get_allowed_processing_per_hour(cls, user_id):
        user_data = await cls.get_or_create_plus(user_id)


        current_data = datetime.now(timezone.utc)
        ending_subscribe_date = user_data.subscribe_ending

        if ending_subscribe_date and ending_subscribe_date > current_data:
            return 50


        if user_data.is_plus:
            await SubscribePlus.objects.filter(user_id=user_id).aupdate(is_plus=False)

        return 10




    class Meta:
        verbose_name_plural = 'Subscription Plus'


    def __str__(self):
        return str(self.user_id)


class Limits(models.Model):
    user_id = models.OneToOneField(TelegramUser, on_delete=models.CASCADE)
    processed_per_hour = models.IntegerField(default=0)
    reset_time = models.DateTimeField(null=True, blank=True)
    is_plus = models.BooleanField(default=False)


    @classmethod
    async def get_or_create_limit(cls, user_id):
        """Вспомогательный метод: находит или автоматически создаёт лимиты для юзера"""
        user_obj = await TelegramUser.objects.aget(pk=user_id)
        limit_obj, _ = await cls.objects.aget_or_create(
            user_id=user_obj,
            defaults={'processed_per_hour': 0, 'reset_time': None}
        )
        return limit_obj


    @classmethod
    async def increase_processed_per_hour(cls, user_id):
        await cls.get_or_create_limit(user_id)
        await Limits.objects.filter(user_id=user_id).aupdate(processed_per_hour=F('processed_per_hour') + 1)


    @classmethod
    async def get_processed_per_hour(cls, user_id):
        await cls.get_or_create_limit(user_id)
        processed_per_hour = await Limits.objects.filter(user_id=user_id).aget()
        return processed_per_hour.processed_per_hour


    @classmethod
    async def reset_processed_per_hour(cls, user_id):
        await cls.get_or_create_limit(user_id)
        await Limits.objects.filter(user_id=user_id).aupdate(processed_per_hour=0)


    @classmethod
    async def set_reset_time(cls, user_id):
        await cls.get_or_create_limit(user_id)
        reset_time = datetime.now(timezone.utc) + timedelta(hours=1)
        await Limits.objects.filter(user_id=user_id).aupdate(reset_time=reset_time)


    @classmethod
    async def reset_limit_time(cls, user_id):
        await cls.get_or_create_limit(user_id)
        await Limits.objects.filter(user_id=user_id).aupdate(reset_time=None)



    @classmethod
    async def get_reset_time(cls, user_id):
        await cls.get_or_create_limit(user_id)
        reset_time = await Limits.objects.filter(user_id=user_id).aget()
        return reset_time.reset_time



    @classmethod
    async def get_data_about_user_limits(cls, user_id):
        await cls.get_or_create_limit(user_id)

        user_data = await Limits.objects.filter(user_id=user_id).aget()

        return [user_data.processed_per_hour, user_data.reset_time]



    class Meta:
        verbose_name_plural = 'Limits'



    def __str__(self):
        return str(self.user_id)