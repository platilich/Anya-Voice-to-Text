from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import GroqAPIKey, StickersAnya




admin.site.register(StickersAnya, SingletonModelAdmin)
admin.site.register(GroqAPIKey)