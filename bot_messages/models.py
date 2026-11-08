from django.db import models
from solo.models import SingletonModel
from bot.logger import logger


from cachetools import TTLCache



cache_messages = TTLCache(maxsize=1000, ttl=180)


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
            "🚀 Fast & accurate – just send a voice or video and I’ll do the rest! ✨"
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
        verbose_name='Recognized count recognised'
    )


    minutes_used_today = models.TextField(
        max_length=255,
        default='🕓 Minutes used today: {used_minutes}/{allowed_minutes}',
        verbose_name='Block how much minutes used'
    )


    text_status_subscribe = models.TextField(
        max_length=255,
        default='⭐ Subscription status: {variable_status}',
        verbose_name='Block subscription status'
    )



    variable_status_days_left = models.TextField(
        max_length=255,
        default='{days} days',
        verbose_name='Days remaining',
    )


    variable_status_end_today = models.TextField(
        max_length=255,
        default='Expires today',
        verbose_name='Subscription expiration notice',
    )

    variable_status_not_active = models.TextField(
        max_length=255,
        default='-',
        verbose_name='Status when inactive',
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
        default="✨ You have {left_days} days of Plus left - enjoy! 💖",
        verbose_name='Active Plus subscription',
    )

    ending_today = models.TextField(
        max_length=500,
        default="✨ Your Plus subscription expires today. Want to renew? 💫",
        verbose_name='Plus subscription expires today'
    )

    no_subscription = models.TextField(
        max_length=500,
        default="🚀 Want to do more? Upgrade to Plus for higher limits! ✨",
        verbose_name='Plus upgrade prompt'

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
            "📊 <b>Today's limit:</b> {used_time}/{allowed} min used\n"
            "⏰ Your minutes will refresh tomorrow.\n\n"
            "⭐ Need more time? Upgrade to Plus!\n"
            "👉 <b>/get_plus</b>"
        ),
        verbose_name="Daily usage limit reached"
    )


    not_enough_minutes_to_recognize = models.TextField(
        max_length=255,
        default=(
            "❌ Your clip is {duration_voice_message} long, so it won’t fit within today’s remaining limit "
            "({used_time}/{allowed} min used).\n\n"
            "⭐ Need more time? <b>Upgrade to Plus</b>!\n"
            "👉 <b>/get_plus</b>"
        ),
        verbose_name='Daily limit reached for this clip'
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
        default="✨ Voluntary tip to support Anya! 🎁 Bonus: 30 min/hr limit for 30 days. ❤️ Non-refundableю",
        verbose_name="Invoice Description"
    )

    success_purchase = models.TextField(
        max_length=255,
        default=(
            '🎉 Oh, <b>{name}</b>, thank you so much for supporting me! 💖\n\n'
            '✅ Received: {payment_info.total_amount} ⭐\n\n'
            '🚀 I’ve upgraded your limits to 30 minutes per hour for 1 month. Enjoy!'
        ),
        verbose_name="Success Purchase Message ({name}, {payment_info.total_amount})"
    )


    ref_link_success_new_user = models.TextField(
        max_length=255,
        default=(
            "🎉 <b>{name}</b>, you followed a friend's link!!\n\n"
            "✅ You have a free Plus for a month! ⭐\n\n"
            '🚀 Your limits to 30 minutes per hour for 1 month. Enjoy!'
        ),
        verbose_name="Greeting a user who clicked on a friend's link"
    )


    ref_link_success_owner = models.TextField(
        max_length=255,
        default=(
            "🎉 <b>{name}</b>, your friend came through your link!\n\n"
            "✅ You have a free Plus for a month! ⭐\n\n"
            '🚀 Your limits to 30 minutes per hour for 1 month. Enjoy!'
        ),
        verbose_name="A message that a friend has successfully clicked on the link"
    )


    def __str__(self):
        return 'Subscription Payment Texts'

    class Meta:
        verbose_name = 'Subscription Payment'
        verbose_name_plural = 'Subscription Payments'




class Buttons(BaseSingletonMessage):
    button_summarize_title = models.TextField(
        max_length=255,
        default='✨ Summarize',
        verbose_name='The name of the summary button (shorten the text, for voice messages where there are > 50 words)'
    )


    button_copy_title = models.TextField(
        max_length=255,
        default='❤️ Copy',
        verbose_name='The name of copy button in the profile'
    )


    button_pay_title = models.TextField(
        max_length=255,
        default="✅ Pay",
        verbose_name='Button pay'
    )


    button_terms_title = models.TextField(
        max_length=255,
        default="📝 Terms",
        verbose_name='Button terms'
    )

    button_forward_title = models.TextField(
        max_length=255,
        default='✨ Share'
    )




    def __str__(self):
        return 'ButtonSummarize'




class ErrorMessages(BaseSingletonMessage):
    # texts for errors and system notices

    admin_no_groq_keys = models.TextField(
        max_length=500,
        default=(
            "⚠️ I can’t process requests right now—my Groq API keys are invalid, blocked, or out of quota.\n"
            "👉 <i>Please add or update a key in the admin area so I can get back to work!</i>"
        ),
        verbose_name='Groq API keys unavailable',
    )

    service_unavailable = models.TextField(
        max_length=255,
        default="😔 Oops, I can’t process audio right now. Please try again in a little while!",
        verbose_name='Audio processing temporarily unavailable',

    )

    failed_payment = models.TextField(
        max_length=255,
        default=(
            "⚠️ Looks like the price changed, or the payment was made in a different currency. "
            "I’ll send the money back to your account.\n\n"
            "Please get a new invoice with /get_plus."
        ),
        verbose_name='Price change or currency mismatch notice',

    )


    refund_payment = models.TextField(
        max_length=255,
        default='✅ All sorted!\nI’ve sent the money back to your account.',
        verbose_name='Refund confirmation'

    )



    class Meta:
        verbose_name = 'Error Text'
        verbose_name_plural = 'Error Texts'



    def __str__(self):
        return 'Error Texts'




async def get_text(model, key):
    cache_key = (model._meta.label_lower, key)

    if cache_key in cache_messages:
        return cache_messages[cache_key]

    text = await model.get_message_text(key)
    cache_messages[cache_key] = text
    return text