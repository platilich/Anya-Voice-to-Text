from django.db import models
from solo.models import SingletonModel
from cachetools import TTLCache


cache_messages = TTLCache(maxsize=2, ttl=180)


# Create your models here.
class StartMessageSettings(SingletonModel):
    # texts for /start command and welcome screen
    start_text = models.TextField(
        default=(
            "👋 Hi, <b>{name}</b>! I’m <b>Anya</b> 😊\n\n"
            "🔊 Voice messages and 📽️ videos, turned into text.\n\n"
            "✨ Send one my way!"
        ),

        verbose_name='Start Message Text'
    )


    start_text_invited_user = models.TextField(
        default=(
            "👋 Hi, <b>{name}</b>! I’m <b>Anya</b> 😊\n\n"
            "🔊 I’ll turn your voice messages into text;\n"
            "📽️ and transcribe your Telegram videos.\n\n"
            "🎁 You came through a friend’s link, so here are 3 bonus minutes!\n"
            "⏱️ You now have <b>6 minutes</b> to use 💛\n\n"
            "🚀 Send me a voice message or video, and I’ll get right on it! ✨"
        ),

        verbose_name='Start Message Text'
    )



    def __str__(self):
        return 'Handler /start message settings'



    class Meta:
        verbose_name = 'Handler /start message settings'
        verbose_name_plural = 'Handler /start message settings'




async def get_text_for_start_message(key: str):
    if key in cache_messages:
        return cache_messages[key]

    result, created = await StartMessageSettings.objects.aget_or_create()


    cache_messages[key] = getattr(result, key)

    return cache_messages[key]