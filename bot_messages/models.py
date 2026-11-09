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


    left_seconds = models.TextField(
        max_length=255,
        default='🕓 Balance: {left_seconds} seconds',
        verbose_name='How much minutes used'
    )

    about_limits = models.TextField(
        max_length=255,
        default='⏳ 3 minutes are added every 24 hours',
        verbose_name='About limit'
    )


    text_suggest_invite_friend = models.TextField(
        max_length=255,
        default='🎁 You can get a 3 minutes!\n📋 Just tap the button below and send it to a friend.',
        verbose_name='Suggest invite friend'
    )




    def __str__(self):
        return 'Profile Texts'


    class Meta:
        verbose_name = 'Profile Message'
        verbose_name_plural = 'Profile Messages'



class LimitMessages(BaseSingletonMessage):
    # texts for hourly limit refresh timers
    limit = models.TextField(
        max_length=255,
        default=(
            "👋 Hey, {name}!\n"
            "⏰ You've used up your minutes for now. Your free 3 minutes refresh every 24 hours.\n\n"
            "⭐ Need more right now? Invite a friend who's new to the bot! Tap the button below and send them your link. "
            "As soon as they press Start, you'll both get an extra 3 minutes.\n"
        ),
        verbose_name="Daily usage limit reached"
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




class DonateMessages(BaseSingletonMessage):
    # texts for invoicing and successful payments
    invoice_title = models.TextField(
        max_length=255,
        default="Support the project with Anya",
        verbose_name="Invoice Title"
    )

    invoice_description = models.TextField(
        default="A small donation to support the project — 1 star.",
        verbose_name="Invoice Description"
    )

    success_donate = models.TextField(
        max_length=255,
        default=(
            "✨ {name}, thanks so much for the donation! ❤️"
        ),
        verbose_name="Success Purchase Message ({name}, {payment_info.total_amount})"
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


    button_gift_one_star = models.TextField(
        max_length=255,
        default="❤️ Gift 1 ⭐",
        verbose_name='Gift btn'
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




class ReferenceTexts(SingletonModel):
    admin_no_groq_keys = models.TextField(
        max_length=500,
        default=(
            "Enjoy 3 free minutes—you’ve arrived via a friend’s link!"
        ),
        verbose_name='Groq API keys unavailable',
    )

    service_unavailable = models.TextField(
        max_length=255,
        default="Your friend followed the link! Here are 3 minutes for you!",
        verbose_name='Audio processing temporarily unavailable',

    )


    class Meta:
        verbose_name = 'Reference texts'
        verbose_name_plural = 'Reference texts'



    def __str__(self):
        return 'Reference texts'





async def get_text(model, key):
    cache_key = (model._meta.label_lower, key)

    if cache_key in cache_messages:
        return cache_messages[cache_key]

    text = await model.get_message_text(key)
    cache_messages[cache_key] = text
    return text