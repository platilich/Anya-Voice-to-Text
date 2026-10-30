from django.db import models
from solo.models import SingletonModel

# --- caching of data in RAM ---
from cachetools import TTLCache



# --- we store the data ---

# --- for 2 minutes ---
cache_subscription = TTLCache(maxsize=1, ttl=120)

# --- for 3 minutes ---
cache_protection = TTLCache(maxsize=1, ttl=180)



class SubscriptionPrice(SingletonModel):
    price = models.IntegerField(
        blank=True,
        default=3,
        verbose_name='Subscription price Plus. (Updated within 2 minutes)'
    )


    class Meta:
        verbose_name_plural = 'SubscriptionPrice'


    def __str__(self):
        return 'SubscriptionPlus'


async def get_price_subscription():
    # --- if the value is in the cache, we return it ---
    if "price" in cache_subscription:
        return cache_subscription["price"]

    # --- getting a new value from the database ---
    result = await SubscriptionPrice.objects.aget()

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



async def get_rest_time():
    # --- if the value is in the cache, we return it ---
    if "rest" in cache_protection:
        return cache_protection["rest"]


    # --- getting a new value from the database ---
    result = await Protection.objects.aget()

    # --- cached to reduce database load ---
    cache_protection["rest"] = float(result.rest_time)

    return float(result.rest_time)




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


        async for key in cls.objects.all():
            keys.append(key)



        # --- returning the keys in the dictionary ---
        return keys


    class Meta:
        verbose_name_plural = 'Groq API Keys'


    def __str__(self):
        return self.name