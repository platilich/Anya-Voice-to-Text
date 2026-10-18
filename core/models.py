from django.db import models


# Create your models here.
class Messages(models.Model):
    hello = models.CharField(max_length=255, blank=True, verbose_name='/start')

    plus_ending_today = models.CharField(max_length=255, blank=True, verbose_name='plus_ending_today')
    user_did_not_buy_subscribe = models.CharField(max_length=255, blank=True, verbose_name='user_did_not_buy_subscribe')


    @classmethod
    async def get_message_text(cls, message_name):
        default_values = {
            # command start
            'hello': (
                f"👋 Hey, <b>name</b>! I'm <b>Anya</b> ✨\n\n"
                "I'm here to instantly transcribe your audio & video into clear text! 🎧\n\n"
                "<b>Here is what I can do:</b>\n"
                "🎙️ Convert voice notes & audio files to text\n"
                "🎥 Transcribe Telegram video messages (circles)\n\n"
                "⚡ Fast, accurate, and super easy to use!\n\n"
                "<b>Ready to get started?</b> Just send or forward me any voice note or video message! 💫\n\n"
                "<a href='https://github.com/platilich/NoteCircle'><b>GitHub</b></a>"
            ),


            # command profile
            'plus_ending_today': '⏰ <b>Your Plus subscription expires today!</b> Don\'t forget to renew it! ✨\n\n',
            'user_did_not_buy_subscribe': '✨ <b>Want more limits?</b>\n🚀 Upgrade to Plus for 5х higher limits (50 req/hr)!\n👉 <b>/get_plus</b>',

        }

        """Получаем или создаем запись с дефолтными значениями"""
        stickers, _ = await cls.objects.aget_or_create(
            pk=1,
            defaults=default_values
        )


        """Проверяем нужное поле: если оно пустое, возвращаем дефолт и сохраняем в бд"""
        val = getattr(stickers, message_name, None)
        if not val:
            val = default_values.get(message_name, '')
            setattr(stickers, message_name, val)
            await stickers.asave(update_fields=[message_name])

        return val


    class Meta:
        verbose_name_plural = 'Setting messages'

    def __str__(self):
        return 'Stickers'





class StickersAnya(models.Model):
    hello = models.CharField(max_length=255, blank=True, verbose_name='Hello sticker ID')
    profile = models.CharField(max_length=255, blank=True, verbose_name='Profile sticker ID')
    recognising = models.CharField(max_length=255, blank=True, verbose_name='Recognising sticker ID')
    limits = models.CharField(max_length=255, blank=True, verbose_name='Limits sticker ID')
    oops = models.CharField(max_length=255, blank=True, verbose_name='Error sticker ID')
    love = models.CharField(max_length=255, blank=True, verbose_name='Love sticker ID')
    plus = models.CharField(max_length=255, blank=True, verbose_name='Plus sticker ID')



    @classmethod
    async def get_sticker(cls, sticker_name):
        default_values = {
            'hello': 'CAACAgIAAxkBAAEHrdZq1JhcL9T5pa77J9Z7uBg3DjgP0AACU68AAmxMqEoJDeJY8k3EKD0E',
            'profile': 'CAACAgIAAxkBAAEHra1q1JOTVPzR0LDIs3LZ7FEDVdohxQAC8K8AAt34mUqEkU5x5QKCez0E',
            'recognising': 'CAACAgIAAxkBAAEHratq1JONrnju-xz1U08jxiEiXcW45AACRLQAAuPjoEqTDdiunLpJ3z0E',
            'limits': 'CAACAgIAAxkBAAEHralq1JN0DTsk_Rhphofplj2-aWkRLwACSK8AAvqWoUpMTkweD7RZIz0E',
            'oops': 'CAACAgIAAxkBAAEHraJq1JNYhLGDx5ipkjrueaEbX-2tiwAC_bAAAsc-oUr5baKLCQtl5z0E',
            'love': 'CAACAgIAAxkBAAEHrZFq1I7ory-A1g1vXaHuR-dWECe9dgACjKcAAtzWmEq2xPHDumnrbz0E',
            'plus': 'CAACAgIAAxkBAAIDbWrUnl7XxlpT1W8TilAuhRCyb273AAKbqgACjfOhSnEla-PaMrD9PQQ',
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