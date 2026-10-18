from django.contrib import admin
from .models import TelegramUser, Limits, SubscribePlus


# Register your models here.
admin.site.register(TelegramUser)
admin.site.register(SubscribePlus)
admin.site.register(Limits)