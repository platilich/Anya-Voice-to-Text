from django.db import models
from cachetools import TTLCache
from solo.models import SingletonModel


selected_models = TTLCache(maxsize=2, ttl=180)
cache_text_transcription = TTLCache(maxsize=3, ttl=180)



# Create your models here.
class TranscriptionMessageSettings(SingletonModel):
    new_attempt_recognise = models.TextField(
        max_length=500,
        default='This voice message will be processed a little longer, please wait.',
        verbose_name='A message that there will be another attempt to recognize it. If Gemini has issued a time limit'
    )


    gemini_limits_ended = models.TextField(
        max_length=500,
        default='Today we have run out of limits on our Google AI API account, come back tomorrow',
        verbose_name='A message to the user about our limits from Gemini API'
    )


    gemini_limits_ended_for_admin = models.TextField(
        max_length=500,
        default='The limits on our Gemini AI API account have ended...',
        verbose_name='Message to the admin about Gemini API limits'
    )


    service_unavailable = models.TextField(
        max_length=255,
        default="😔 Oops, I can’t process audio right now. Please try again in a little while!",
        verbose_name='Audio processing temporarily unavailable',

    )


    admin_no_keys = models.TextField(
        max_length=500,
        default=(
            "⚠️ I can’t process requests right now—my Groq API keys are invalid, blocked, or out of quota.\n"
            "👉 <i>Please add or update a key in the admin area so I can get back to work!</i>"
        ),
        verbose_name='Groq API keys unavailable',
    )



    class Meta:
        verbose_name = "Transcription message Settings"
        verbose_name_plural = 'Transcription message Settings'



    def __str__(self):
        return 'Transcription message Settings'




async def get_api_texts_limitation(key: str):
    # --- if the value is in the cache, we return it ---
    if key in cache_text_transcription:
        return cache_text_transcription[key]

    # --- getting a new value from the database ---
    result, created = await TranscriptionMessageSettings.objects.aget_or_create()

    # --- cached to reduce database load ---
    cache_text_transcription[key] = getattr(result, key)

    return cache_text_transcription[key]




class SelectedModels(SingletonModel):
    voice_processing_model = models.CharField(max_length=50, default='gemini-3.5-transcribe', verbose_name='Current a model for message recognition')
    text_processing_model = models.CharField(max_length=50, default= 'gemini-3.1-flash-lite',verbose_name='Current a model for shortening text')



    def __str__(self):
        return 'Selected models for works'


    class Meta:
        verbose_name = 'Selected model'
        verbose_name_plural = 'Selected models'




async def get_selected_models(type_model: str):
    data = await SelectedModels.aget_solo()

    if type_model == 'voice':
        return data.voice_processing_model


    if type_model == 'text':
        return data.text_processing_model


    return data




class GeminiAPI(models.Model):
    name = models.CharField(max_length=30, verbose_name='Key name')
    api_key = models.CharField(max_length=255, verbose_name='Insert a spare API key (from groq.com)')



    def __str__(self):
        return self.name


    class Meta:
        verbose_name_plural = 'Groq API Keys'




async def get_api_keys():
    keys = []


    async for key in GeminiAPI.objects.all():
        keys.append(key.api_key)


    # --- returning the keys in the dictionary ---
    return keys