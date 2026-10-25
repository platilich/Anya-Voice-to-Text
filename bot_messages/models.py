from django.db import models
from solo.models import SingletonModel





class BaseSingletonMessage(SingletonModel):
    """Базовый класс для всех одиночных моделей с текстами,
    чтобы автоматически поддерживать асинхронное получение полей."""

    @classmethod
    async def get_message_text(cls, field_name: str, **kwargs) -> str:
        # aget_or_create — асинхронный метод Django ORM для получения или создания записи
        config, _ = await cls.objects.aget_or_create(pk=1)

        if not hasattr(config, field_name):
            raise AttributeError(f"{cls.__name__} has no field '{field_name}'")

        value = getattr(config, field_name)

        # подставляем переменные ({name}, {recognised} и т. д.), если они переданы
        return value.format(**kwargs) if kwargs else value

    class Meta:
        abstract = True



class StartMessages(BaseSingletonMessage):
    # texts for /start command and welcome screen
    start_text = models.TextField(
        default=(
            f"👋 Hey, <b>{{name}}</b>! I'm <b>Anya</b> ✨\n\n"
            "I'm always here to help you instantly transcribe your audio & video into clear text! 🎧\n\n"
            "<b>What I can do for you:</b>\n"
            "🎙️ Convert voice notes & audio files to text\n"
            "🎥 Transcribe your Telegram video messages (circles)\n\n"
            "⚡ Fast, accurate, and super easy to use!\n\n"
            "<b>Ready?</b> Just send or forward me any voice note or video message and I'll handle the rest! 💫\n\n"
            "<a href='https://github.com/platilich/Anya-voice-to-text'><b>GitHub</b></a>"
        ),
        verbose_name='Start Message Text'
    )

    def __str__(self):
        return 'Start Command Texts'

    class Meta:
        verbose_name = 'Start Command'
        verbose_name_plural = 'Start Command'




class ProfileMessages(BaseSingletonMessage):
    """Texts for user profile header and stats"""

    header = models.TextField(
        max_length=255,
        default='👋 Hey {name}! Here is everything I know about your stats so far: 🎧\n',
        verbose_name='Header ({name})'
    )

    statistic = models.TextField(
        max_length=255,
        default='🎙 Total items recognized by me: {recognised}',
        verbose_name='Recognized Count ({recognised})'
    )

    def __str__(self):
        return 'Profile Texts'

    class Meta:
        verbose_name = 'Profile Message'
        verbose_name_plural = 'Profile Messages'




class SubscriptionStatusMessages(BaseSingletonMessage):
    """Texts for user subscription status inside profile"""

    active_plus = models.TextField(
        max_length=255,
        default='✨ Plus: {left_days} day left. We’re in this together!',
        verbose_name='Active Plus ({left_days})'
    )

    ending_today = models.TextField(
        max_length=500,
        default="✨ My favorite Plus status ends today! Time to renew?",
        verbose_name='Plus Ending Today'
    )

    no_subscription = models.TextField(
        max_length=500,
        default='🚀 Unlock Plus with me to boost your limits by 5 times!',
        verbose_name='No Subscription Upsell'
    )

    def __str__(self):
        return 'Subscription Status Texts'

    class Meta:
        verbose_name = 'Subscription Status Text'
        verbose_name_plural = 'Subscription Status Texts'




class LimitMessages(BaseSingletonMessage):
    # texts for hourly limit refresh timers
    limit = models.TextField(
        max_length=255,
        default=(
            "📊 <b>Limits:</b> {used_time}/{allowed} minutes\n"
            f"⏳ <b>The limits will be updated tomorrow</b> min\n\n"
            f"⭐ <b>Upgrade to Plus</b> for higher limits!\n"
            '👉 <b>/get_plus</b>'
        ),
        verbose_name='A message telling you that the voice message is too long'
    )


    too_long = models.TextField(
        max_length=255,
        default='⌛ Oh, what a long voice message! 🙈 My servers might run out of RAM from a marathon like that. Let’s keep it under 15 minutes max, alright? ✨',
        verbose_name='A message telling you that the voice message is too long'
    )


    def __str__(self):
        return 'Limit Texts'

    class Meta:
        verbose_name = 'Limit Text'
        verbose_name_plural = 'Limit Texts'




class SubscriptionPlusMessages(BaseSingletonMessage):
    # texts for invoicing and successful payments

    invoice_title = models.TextField(
        max_length=255,
        default="⭐ Support Anya (Plus)",
        verbose_name="Invoice Title"
    )

    invoice_description = models.TextField(
        default="✨ Voluntary tip to support Anya! 🎁 Bonus: 50 req/hr limit for 30 days. ❤️ Non-refundable. 📝 Terms: https://telegra.ph/Terms-of-Service--Refund-Policy-10-17",
        verbose_name="Invoice Description"
    )

    success_purchase = models.TextField(
        max_length=255,
        default=(
            '🎉 Oh, <b>{name}</b>, thank you so much for supporting me! 💖\n\n'
            '✅ Received: {payment_info.total_amount} ⭐\n\n'
            '🚀 I’ve upgraded your limits to 50 processings per hour for 1 month. You rock!'
        ),
        verbose_name="Success Purchase Message ({name}, {payment_info.total_amount})"
    )

    def __str__(self):
        return 'Subscription Payment Texts'

    class Meta:
        verbose_name = 'Subscription Payment'
        verbose_name_plural = 'Subscription Payments'




class ErrorMessages(BaseSingletonMessage):
    # texts for errors and system notices


    admin_no_groq_keys = models.TextField(
        max_length=500,
        default='Oops! All of my Groq API keys are invalid, blocked, or out of limits..\n👉 <i>Please add a new key in the admin area so I can keep working for everyone!</i>',
        verbose_name='Admin Notice: Groq Keys Depleted'
    )

    service_unavailable = models.TextField(
        max_length=255,
        default='😔 Oh no! My audio recognition service is resting right now.\n🙏 Please try again a bit later, I’ll be waiting!',
        verbose_name='User Notice: Service Unavailable'
    )

    def __str__(self):
        return 'Error Texts'

    class Meta:
        verbose_name = 'Error Text'
        verbose_name_plural = 'Error Texts'




async def get_text(model, key):
    text = await model.get_message_text(key)


    return text