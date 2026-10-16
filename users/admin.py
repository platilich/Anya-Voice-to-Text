from django.contrib import admin
from .models import TelegramUser, CustomizeMessages, GroqAPIKey


# Register your models here.

@admin.register(CustomizeMessages)
class CustomMessage(admin.ModelAdmin):
    list_display = ('command_start', 'time_limit', 'error')

    def has_add_permission(self, request):
        return self.model.objects.count() < 1


admin.site.register(TelegramUser)
admin.site.register(GroqAPIKey)