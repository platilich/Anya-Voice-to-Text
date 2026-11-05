from django.db import models
from django.utils import duration
from solo.models import SingletonModel
from bot.logger import logger



class BaseSingletonMessage(SingletonModel):
    """Base class for all single models with texts,
        to automatically support asynchronous field retrieval.
    """

    @classmethod
    async def get_message_text(cls, field_name: str, **kwargs) -> str:
        # aget_or_create — асинхронный метод Django ORM для получения или создания записи
        config, created = await cls.objects.aget_or_create(pk=1)

        if created:
            logger.info(f'created {cls.__name__} in db')

        if not hasattr(config, field_name):
            logger.info(f'no field {field_name} | {cls.__name__}')
            raise AttributeError(f"{cls.__name__} has no field '{field_name}'")

        value = getattr(config, field_name)

        if not value:
            logger.info(f'empty text {field_name} | {cls.__name__}')

        # подставляем переменные ({name}, {recognised} и т. д.), если они переданы
        if not kwargs:
            return value

        try:
            return value.format(**kwargs)
        except Exception as e:
            logger.info(f'failed format {field_name} | {cls.__name__}: {e}')
            raise

    class Meta:
        abstract = True



class StartMessages(BaseSingletonMessage):
    # texts for /start command and welcome screen
    start_text = models.TextField(
        default=(
            f"👋 Hey <b>{{name}}</b>, I’m <b>Anya</b> 🌈\n\n"
            "🔊 Convert voice notes to text;\n"
            "📽️ Transcribe Telegram videos;\n\n"
            "🚀 Fast & accurate – just send a voice or video and I’ll do the rest! ✨\n\n"
            "<a href='httpshttps://github.com/platilich/Anya-voice-to-text'><b>GitHub</b></a>"
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
        default="👋 Hey <b>{name}</b>! Here’s everything I know about your stats so far 🎯\n",
        verbose_name='Header ({name})'
    )

    statistic = models.TextField(
        max_length=255,
        default="🎙️ Total items I’ve recognized for you: <b>{recognised}</b> ✨",
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
        default="✨ {left_days} day{'s' if int(left_days)!=1 else ''} left — we’ve got this! 💖",
        verbose_name='Active Plus ({left_days})'
    )

    ending_today = models.TextField(
        max_length=500,
        default="✨ My Plus expires today—time to renew? 💫",
        verbose_name='Plus Ending Today'
    )

    no_subscription = models.TextField(
        max_length=500,
        default="🚀 Unlock Plus with me and multiply your limits x 5! ✨",
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
            "📊 <b>Limits:</b> {used_time}/{allowed} min\n"
            "⏰ New limits refresh tomorrow\n\n"
            "⭐ <b>Upgrade to Plus</b> for more power!\n"
            "👉 <b>/get_plus</b>"
        ),
        verbose_name='The message that the package of minutes for the day is over'
    )


    not_enough_minutes_to_recognize = models.TextField(
        max_length=255,
        default=(
            "❌ Your clip is {duration_voice_message} long — limit: {used_time}/{allowed} min\n\n"
            "⭐ Want more room? <b>Upgrade to Plus</b>!\n"
            "👉 <b>/get_plus</b>"
        ),
        verbose_name='The message that the voice message does not fit into the daily limit'
    )


    too_long = models.TextField(
        max_length=255,
        default="⌛ Oof, that’s a marathon! 🙈 My servers can’t handle >15 min. Keep it short, please? ✨",
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




class ButtonSummarize(BaseSingletonMessage):
    button_title = models.TextField(
        max_length=255,
        default='✨ Summarize',
        verbose_name='The name of the summary button (shorten the text, for voice messages where there are > 50 words)'
    )


    def __str__(self):
        return 'ButtonSummarize'




class ErrorMessages(BaseSingletonMessage):
    # texts for errors and system notices

    admin_no_groq_keys = models.TextField(
        max_length=500,
        default='Oops! All of my Groq API keys are invalid, blocked, or out of limits..\n👉 <i>Please add a new key in the admin area so I can keep working for everyone!</i>',
        verbose_name='Admin Notice: Groq Keys Depleted'
    )

    service_unavailable = models.TextField(
        max_length=255,
        default="😔 Oops, my audio brain is on a break. 🙏 Try again in a bit—I'll be right here! ✨",
        verbose_name='User Notice: Service Unavailable'
    )

    def __str__(self):
        return 'Error Texts'

    class Meta:
        verbose_name = 'Error Text'
        verbose_name_plural = 'Error Texts'




async def get_text(model, key):
    logger.info(f'get text {key} | {model.__name__}')
    text = await model.get_message_text(key)


    return text