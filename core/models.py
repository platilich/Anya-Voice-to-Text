from django.db import models
from solo.models import SingletonModel

# Create your models here.
class Messages(SingletonModel):
    # --- start ---
    start = models.TextField(
        default=(
            f"👋 Hey, <b>{{name}}</b>! I'm <b>Anya</b> ✨\n\n"
            "I'm always here to help you instantly transcribe your audio & video into clear text! 🎧\n\n"
            "<b>What I can do for you:</b>\n"
            "🎙️ Convert voice notes & audio files to text\n"
            "🎥 Transcribe your Telegram video messages (circles)\n\n"
            "⚡ Fast, accurate, and super easy to use!\n\n"
            "<b>Ready?</b> Just send or forward me any voice note or video message and I'll handle the rest! 💫\n\n"
            "<a href='https://github.com/platilich/NoteCircle'><b>GitHub</b></a>"
        ),
        verbose_name='Start (/start)'
    )

    # --- profile ---
    profile_header = models.TextField(
        max_length=255,
        default='👋 Hey {name}! Here is everything I know about your stats so far: 🎧\n\n',
        verbose_name='Profile: Header ({name})'
    )

    profile_statistic = models.TextField(
        max_length=255,
        default='🎙 Total items recognized by me: {recognised}',
        verbose_name='Profile: Statistic ({recognised})'
    )

    profile_limit = models.TextField(
        max_length=255,
        default='🔄 Your current hourly limit: {recognised}/{allowed_per_hour}',
        verbose_name='Profile: Limit ({recognised}, {allowed_per_hour})'
    )

    profile_status_subscribe = models.TextField(
        max_length=255,
        default='✨ Plus: {left_days} day left. We’re in this together!',
        verbose_name='Profile: Active Plus ({left_days})'
    )

    profile_status_subscribe_ending_today = models.TextField(
        max_length=500,
        default="✨ My favorite Plus status ends today! Time to renew?",
        verbose_name='Profile: Plus ending today'
    )

    profile_status_no_subscribe = models.TextField(
        max_length=500,
        default='🚀 Unlock Plus with me to boost your limits by 5 times!',
        verbose_name='Profile: No subscription (upsell)'
    )

    # --- update limit ---
    the_limits_will_updated_for = models.TextField(
        max_length=255,
        default='🕜 I will refresh your limits in: {minutes} min.',
        verbose_name='Limits: Update timer in minutes ({minutes})'
    )

    the_limits_will_updated_now = models.TextField(
        max_length=255,
        default='Almost there! Limits will refresh in ~30 seconds ⏱️',
        verbose_name='Limits: Updating now (< 0 min)'
    )

    # --- other ---
    sticker_file_id = models.TextField(
        max_length=50,
        default='ⓘ Sticker ID: {sticker_id}',
        verbose_name='Sticker: File ID ({sticker_id})'
    )

    # --- errors ---
    error_zero_groq_api_keys_for_admin = models.TextField(
        max_length=500,
        default='Oops! All of my Groq API keys are invalid, blocked, or out of limits..\n👉 <i>Please add a new key in the admin area so I can keep working for everyone!</i>',
        verbose_name='Errors: Groq keys out (Admin notice)'
    )

    something_went_wrong = models.TextField(
        max_length=255,
        default='😔 Oh no! My audio recognition service is resting right now.\n🙏 Please try again a bit later, I’ll be waiting!',
        verbose_name='Errors: Service unavailable (User notice)'
    )

    # --- subscribe plus ---
    invoice_title = models.TextField(
        max_length=255,
        default="⭐ Support Anya (Plus)",
        verbose_name="Invoice: Title"
    )


    invoice_description = models.TextField(
        default="✨ Voluntary tip to support Anya! 🎁 Bonus: 50 req/hr limit for 30 days. ❤️ Non-refundable. 📝 Terms: https://telegra.ph/Terms-of-Service--Refund-Policy-10-17",
        verbose_name="Invoice: Description (Short, single line)"
    )


    user_bought_subscribe = models.TextField(
        max_length=255,
        default=(
            '🎉 Oh, <b>{name}</b>, thank you so much for supporting me! 💖\n\n'
            '✅ Received: {payment_info.total_amount} ⭐\n\n'
            '🚀 I’ve upgraded your limits to 50 processings per hour for 1 month. You rock!'
        ),
        verbose_name="Payment: Success message ({name}, {payment_info.total_amount})"
    )



    class Meta:
        verbose_name_plural = "Bot Messages"


    def __str__(self):
        return 'Messages'




    @classmethod
    async def get_message_text(cls, message_name):
        """Получаем или создаем запись с дефолтными значениями"""
        config, _ = await cls.objects.aget_or_create(pk=1)

        value = getattr(config, message_name, None)

        return value







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