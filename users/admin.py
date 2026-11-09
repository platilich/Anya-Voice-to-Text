from django.contrib import admin
from .models import TelegramUser, ReferenceLinks


# Register your models here.
admin.site.register(TelegramUser)
admin.site.register(ReferenceLinks)