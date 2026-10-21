from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import Messages, GroqAPIKey, StickersAnya




admin.site.register(Messages, SingletonModelAdmin)
admin.site.register(StickersAnya, SingletonModelAdmin)


admin.site.register(GroqAPIKey)