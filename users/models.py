from django.db import models
from django.db.models import F, DateTimeField
from datetime import datetime, timezone
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

        except TelegramUser.DoesNotExist:
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





    class Meta:
        verbose_name_plural = 'Subscription Plus'


    def __str__(self):
        return f'Subscription for {self.user_id}'


class Limits(models.Model):
    user_id = models.OneToOneField(TelegramUser, on_delete=models.CASCADE)
    seconds_used = models.IntegerField()
    usage_date = models.DateField(null=True, blank=True)
    is_plus = models.BooleanField(default=False)


    @classmethod
    async def get_or_create_limit(cls, user_id):
        # auxiliary method: finds or automatically creates user limits
        user_obj = await TelegramUser.objects.aget(pk=user_id)
        limit_obj, _ = await cls.objects.aget_or_create(
            user_id=user_obj,
            defaults={'seconds_used': 0}
        )
        return limit_obj



    @classmethod
    async def maybe_reset(cls, user_id: int):
        limit = await cls.get_or_create_limit(user_id)
        today = datetime.now(timezone.utc).date()

        if limit.usage_date != today:
            limit.seconds_used = 0
            limit.usage_date = today
            await limit.asave(update_fields=["seconds_used", "usage_date"])



    @classmethod
    async def get_seconds_used(cls, user_id: int): # возращает количество использованных сегодня минут
        limit = await cls.get_or_create_limit(user_id)

        return limit.seconds_used



    @classmethod
    async def get_daily_limit_time(cls, user_id):
        status = await SubscribePlus.get_or_create_plus(user_id=user_id)


        if status.is_plus:
            return f"{30:02d}:{00:02d}"

        else:
            return f"{15:02d}:{00:02d}"





    @classmethod
    async def spend_seconds(cls, user_id, duration_seconds):
        await cls.maybe_reset(user_id) # проверяем дату если дата совпадет то сбрасываем


        await cls.objects.filter(user_id=user_id).aupdate(
            seconds_used=F("seconds_used") + duration_seconds
        )



    @classmethod
    async def return_seconds(cls, user_id, duration_seconds):
        await cls.objects.filter(user_id=user_id).aupdate(
            seconds_used=F('seconds_used') - duration_seconds
        )


    @classmethod
    async def get_usage_for_profile(cls, user_id):
        await cls.maybe_reset(user_id) # получаем лимит сколько мы можем использовали


        time_used = await cls.get_seconds_used(user_id)
        max_minutes = await cls.get_daily_limit_time(user_id)


        minutes = time_used // 60
        seconds = time_used % 60

        time_formatted = f"{minutes:02d}:{seconds:02d}"


        return time_formatted, max_minutes




    class Meta:
        verbose_name_plural = 'Limits'



    def __str__(self):
        return str(self.user_id)