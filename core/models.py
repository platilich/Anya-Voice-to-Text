from django.db import models
from solo.models import SingletonModel


# Create your models here.
class StickersAnya(SingletonModel):
    hello = models.CharField(
        max_length=255,
        blank=True,
        default='CAACAgIAAxkBAAEHrdZq1JhcL9T5pa77J9Z7uBg3DjgP0AACU68AAmxMqEoJDeJY8k3EKD0E',
        verbose_name='Hello sticker ID'
    )

    profile = models.CharField(
        max_length=255,
        blank=True,
        default='CAACAgIAAxkBAAEHra1q1JOTVPzR0LDIs3LZ7FEDVdohxQAC8K8AAt34mUqEkU5x5QKCez0E',
        verbose_name='Profile sticker ID'
    )

    recognising = models.CharField(
        max_length=255,
        blank=True,
        default='CAACAgIAAxkBAAEHratq1JONrnju-xz1U08jxiEiXcW45AACRLQAAuPjoEqTDdiunLpJ3z0E',
        verbose_name='Recognising sticker ID'
    )


    limits = models.CharField(
        max_length=255,
        blank=True,
        default='CAACAgIAAxkBAAEHralq1JN0DTsk_Rhphofplj2-aWkRLwACSK8AAvqWoUpMTkweD7RZIz0E',
        verbose_name='Limits sticker ID'
    )


    oops = models.CharField(
        max_length=255,
        blank=True,
        default='CAACAgIAAxkBAAEHraJq1JNYhLGDx5ipkjrueaEbX-2tiwAC_bAAAsc-oUr5baKLCQtl5z0E',
        verbose_name='Error sticker ID'
    )

    love = models.CharField(
        max_length=255,
        blank=True,
        default='CAACAgIAAxkBAAEHrZFq1I7ory-A1g1vXaHuR-dWECe9dgACjKcAAtzWmEq2xPHDumnrbz0E',
        verbose_name='Love sticker ID'
    )


    plus = models.CharField(
        max_length=255,
        blank=True,
        default='CAACAgIAAxkBAAIDbWrUnl7XxlpT1W8TilAuhRCyb273AAKbqgACjfOhSnEla-PaMrD9PQQ',
        verbose_name='Plus sticker ID'
    )



    @classmethod
    async def get_sticker(cls, message_name):
        """Получаем или создаем запись с дефолтными значениями"""
        config, _ = await cls.objects.aget_or_create(pk=1)

        value = getattr(config, message_name, None)

        return value



    class Meta:
        verbose_name_plural = 'Stickers with Anya'



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