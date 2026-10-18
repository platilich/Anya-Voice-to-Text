from django.contrib import admin
from .models import TelegramUser, ManageBot, GroqAPIKey, Limits, SubscribePlus, Stickers


# Register your models here.

@admin.register(ManageBot)
class CustomMessage(admin.ModelAdmin):
    list_display = ('command_start', 'time_limit', 'error')

    def has_add_permission(self, request):
        return self.model.objects.count() < 1


admin.site.register(TelegramUser)
admin.site.register(SubscribePlus)
admin.site.register(GroqAPIKey)
admin.site.register(Stickers)
admin.site.register(Limits)
