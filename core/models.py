from django.db import models
from solo.models import SingletonModel

# --- caching of data in RAM ---
from cachetools import TTLCache



# --- we store the data ---
# --- for 2 minutes ---
cache_subscription = TTLCache(maxsize=1, ttl=120)

# --- for 3 minutes ---
cache_antiflood = TTLCache(maxsize=1, ttl=180)



class DonatePrice(SingletonModel):
    price = models.IntegerField(
        blank=True,
        default=1,
        verbose_name='Donate Price. (Updated within 2 minutes)'
    )


    class Meta:
        verbose_name_plural = 'Donate price'


    def __str__(self):
        return 'Donate price'



    @classmethod
    async def get_donate_price(cls):
        # --- if the value is in the cache, we return it ---
        if "price" in cache_subscription:
            return cache_subscription["price"]

        # --- getting a new value from the database ---
        result = await cls.objects.aget()

        # --- cached to reduce database load ---
        cache_subscription["price"] = result.price

        return result.price





class Protection(SingletonModel):
    rest_time = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        blank=True,
        default=2.0,
        verbose_name='Flood protection. The time of ignoring the user during spam. (Updated within 3 minutes)'
    )


    class Meta:
        verbose_name = 'Protection'
        verbose_name_plural = 'Protection'



    def __str__(self):
        return 'Protection'


    @classmethod
    async def get_rest_time(cls):
        # --- if the value is in the cache, we return it ---
        if "rest" in cache_antiflood:
            return cache_antiflood["rest"]


        # --- getting a new value from the database ---
        result = await Protection.objects.aget()

        # --- cached to reduce database load ---
        cache_antiflood["rest"] = float(result.rest_time)

        return float(result.rest_time)





class GroqAPIKey(models.Model):
    name = models.CharField(max_length=30, blank=True, verbose_name='Key name')
    api_key = models.CharField(max_length=255, blank=True, verbose_name='Insert a spare API key (from groq.com)')



    def __str__(self):
        return self.name


    @classmethod
    async def get_api_keys(cls):
        keys = []


        async for key in cls.objects.all():
            keys.append(key)


        # --- returning the keys in the dictionary ---
        return keys


    class Meta:
        verbose_name_plural = 'Groq API Keys'