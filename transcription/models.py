from django.db import models
from cachetools import TTLCache



cache_summarize_button = TTLCache(maxsize=1, ttl=180)


# Create your models here.
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