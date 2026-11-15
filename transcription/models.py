from django.db import models
from cachetools import TTLCache
from solo.models import SingletonModel


selected_models = TTLCache(maxsize=2, ttl=180)



# Create your models here.
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