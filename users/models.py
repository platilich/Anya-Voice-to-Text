from django.db import models
from django.utils import timezone
from django.db.models import F
from datetime import datetime, timedelta, timezone



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
    async def increase_count_count_recognise(cls, user_id):
        await TelegramUser.objects.filter(user_id=user_id).aupdate(count_video=F('count_recognise') + 1)


    @classmethod
    async def change_status_banned(cls, user_id, is_banned):
        await TelegramUser.objects.filter(user_id=user_id).aupdate(is_banned=is_banned)



    @classmethod
    async def banned_user(cls, user_id):
        user = await TelegramUser.objects.filter(user_id=user_id).aget()

        if user.is_banned:
            return True

        return False




    async def can_process_voice(cls, limit=10):
        now = timezone.now()

        if (now - cls.voice_reset_time).total_seconds() > 3600:
            cls.voice_requests_hour = 0
            cls.voice_reset_time = now
            cls.asave(update_fields=["voice_requests_hour", "voice_reset_time"])

        if cls.voice_requests_hour >= limit:
            return False

        await TelegramUser.objects.filter(pk=cls.pk).aupdate(
            voice_requests_hour=F("voice_requests_hour") + 1
        )

        cls.voice_requests_hour += 1
        return True


    def __str__(self):
        return f"{self.name}"



class Limits(models.Model):
    user_id = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    processed_per_hour = models.IntegerField(default=0)
    reset_time = models.DateTimeField(null=True, blank=True)


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




# тут настройка сообщений во всех сообщениях
class CustomizeMessages(models.Model):
    command_start = models.CharField(max_length=255, blank=True, verbose_name='Command /start')
    time_limit = models.CharField(max_length=255, blank=True, verbose_name='Response to video time limit')
    error = models.CharField(max_length=255, blank=True, verbose_name='Error') # Unable to process. Something went wrong.



    @classmethod
    async def get_custom_messages(cls):
        return await CustomizeMessages.objects.aget()



    class Meta:
        verbose_name_plural = 'Customize Messages'


    def __str__(self):
        return 'Customize Messages'



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