from django.contrib.staticfiles.views import serve
from django.db import models
from django.db.models import F, DateTimeField
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta


# Create your models here.
class TelegramUser(models.Model):
    user_id = models.BigIntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=255, blank=True, verbose_name='Name')
    nickname = models.CharField(max_length=255, blank=True, null=True, verbose_name='Nickname')
    count_video = models.PositiveIntegerField(default=0, verbose_name='The number of videos converted into video notes.')
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
    async def increase_count_video(cls, user_id):
        await TelegramUser.objects.filter(user_id=user_id).aupdate(count_video=F('count_video') + 1)


    @classmethod
    async def increase_count_recognise(cls, user_id):
        await TelegramUser.objects.filter(user_id=user_id).aupdate(count_recognise=F('count_recognise') + 1)


    @classmethod
    async def change_status_banned(cls, user_id, is_banned):
        await TelegramUser.objects.filter(user_id=user_id).aupdate(is_banned=is_banned)



    @classmethod
    async def get_statistic(cls, user_id):
        user_data = await TelegramUser.objects.filter(user_id=user_id).aget()

        return [user_data.count_recognise, user_data.count_video, user_data.created_at]




    @classmethod
    async def banned_user(cls, user_id):
        user = await TelegramUser.objects.filter(user_id=user_id).aget()

        if user.is_banned:
            return True

        return False



    def __str__(self):
        return f"{self.name}"




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
        await SubscribePlus.get_or_create_plus(user_id)

        current_time = datetime.now(timezone.utc)
        subscribe_ending_date = current_time + relativedelta(months=1)
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
        await SubscribePlus.get_or_create_plus(user_id)

        left_days = await SubscribePlus.left_days_subscribe(user_id)

        if left_days:
            return left_days

        else:
            return None






    @classmethod
    async def get_allowed_processing_per_hour(cls, user_id):
        user_data = await SubscribePlus.objects.aget(user_id=user_id)


        current_data = datetime.now(timezone.utc)
        ending_subscribe_date = user_data.subscribe_ending

        if ending_subscribe_date:
            if ending_subscribe_date > current_data:
                return 50

            else:
                return 10


        return 10



class Limits(models.Model):
    user_id = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
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






# тут настройка бота
class ManageBot(models.Model):
    command_start = models.CharField(max_length=255, blank=True, verbose_name='Command /start')
    time_limit = models.CharField(max_length=255, blank=True, verbose_name='Response to video time limit')
    error = models.CharField(max_length=255, blank=True, verbose_name='Error')

    @classmethod
    async def get_custom_messages(cls):
        custom_messages, _ = await cls.objects.aget_or_create(
            pk=1,
            defaults={'command_start': '', 'time_limit': '', 'error': ''}
        )
        return custom_messages


    class Meta:
        verbose_name_plural = 'Customize Messages'


    def __str__(self):
        return 'Customize Messages'



class Stickers(models.Model):
    hello = models.CharField(max_length=255, blank=True, verbose_name='Hello sticker ID')
    profile = models.CharField(max_length=255, blank=True, verbose_name='Profile sticker ID')
    recognising = models.CharField(max_length=255, blank=True, verbose_name='Recognising sticker ID')
    limits = models.CharField(max_length=255, blank=True, verbose_name='Limits sticker ID')
    oops = models.CharField(max_length=255, blank=True, verbose_name='Error sticker ID')
    love = models.CharField(max_length=255, blank=True, verbose_name='Love sticker ID')


    @classmethod
    async def get_sticker(cls, sticker_name):
        default_values = {
            'hello': 'CAACAgIAAxkBAAEHrdZq1JhcL9T5pa77J9Z7uBg3DjgP0AACU68AAmxMqEoJDeJY8k3EKD0E',
            'profile': 'CAACAgIAAxkBAAEHra1q1JOTVPzR0LDIs3LZ7FEDVdohxQAC8K8AAt34mUqEkU5x5QKCez0E',
            'recognising': 'CAACAgIAAxkBAAEHratq1JONrnju-xz1U08jxiEiXcW45AACRLQAAuPjoEqTDdiunLpJ3z0E',
            'limits': 'CAACAgIAAxkBAAEHralq1JN0DTsk_Rhphofplj2-aWkRLwACSK8AAvqWoUpMTkweD7RZIz0E',
            'oops': 'CAACAgIAAxkBAAEHraJq1JNYhLGDx5ipkjrueaEbX-2tiwAC_bAAAsc-oUr5baKLCQtl5z0E',
            'love': 'CAACAgIAAxkBAAEHrZFq1I7ory-A1g1vXaHuR-dWECe9dgACjKcAAtzWmEq2xPHDumnrbz0E',
        }

        """Получаем или создаем запись с дефолтными значениями"""
        stickers, _ = await cls.objects.aget_or_create(
            pk=1,
            defaults=default_values
        )


        """Проверяем нужное поле: если оно пустое, возвращаем дефолт и сохраняем в бд"""
        val = getattr(stickers, sticker_name, None)
        if not val:
            val = default_values.get(sticker_name, '')
            setattr(stickers, sticker_name, val)
            await stickers.asave(update_fields=[sticker_name])

        return val


    class Meta:
        verbose_name_plural = 'Stickers'

    def __str__(self):
        return 'Stickers'





class GroqAPIKey(models.Model):
    name = models.CharField(max_length=30, blank=True, verbose_name='Key name')
    api_key = models.CharField(max_length=255, blank=True, verbose_name='Insert a spare API key (from groq.com)')



    @classmethod
    async def get_api_keys(cls):
        keys = []
        # async for автоматически выполнит асинхронный запрос к БД
        async for key in cls.objects.all():
            keys.append(key)

        return keys


    class Meta:
        verbose_name_plural = 'Groq API Keys'


    def __str__(self):
        return self.name