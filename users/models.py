from django.db import models
from django.utils import timezone
from django.db.models import F


# Create your models here.
class TelegramUser(models.Model):
    user_id = models.BigIntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=255, blank=True, verbose_name='Name')
    nickname = models.CharField(max_length=255, blank=True, null=True, verbose_name='Nickname')
    count_video = models.PositiveIntegerField(default=0, verbose_name='The number of videos converted into video notes.')
    count_recognise = models.PositiveIntegerField(default=0, verbose_name='Number of processed voice messages/video notes into text')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Registered')
    is_banned = models.BooleanField(default=False, verbose_name='Banned')

    voice_requests_hour = models.PositiveIntegerField(default=0)
    voice_reset_time = models.DateTimeField(default=timezone.now)


    class Meta:
        verbose_name_plural = "Telegram users"


    async def can_process_voice(self, limit=10):
        now = timezone.now()

        if (now - self.voice_reset_time).total_seconds() > 3600:
            self.voice_requests_hour = 0
            self.voice_reset_time = now
            await self.asave(update_fields=["voice_requests_hour", "voice_reset_time"])

        if self.voice_requests_hour >= limit:
            return False

        await TelegramUser.objects.filter(pk=self.pk).aupdate(
            voice_requests_hour=F("voice_requests_hour") + 1
        )
        self.voice_requests_hour += 1
        return True


    def __str__(self):
        return f"{self.name} - {self.user_id}"





# тут настройка сообщений во всех сообщениях
class CustomizeMessages(models.Model):
    command_start = models.CharField(max_length=255, blank=True, verbose_name='Command /start')
    time_limit = models.CharField(max_length=255, blank=True, verbose_name='Response to video time limit')
    error = models.CharField(max_length=255, blank=True, verbose_name='Error') # Unable to process. Something went wrong.


    class Meta:
        verbose_name_plural = 'Customize Messages'


    def __str__(self):
        return 'Customize Messages'