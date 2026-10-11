from django.contrib import admin
from .models import TelegramUser, CustomizeMessages


# Register your models here.
admin.site.register(TelegramUser)


@admin.register(CustomizeMessages)
class CustomMessage(admin.ModelAdmin):
    list_display = ('command_start', 'time_limit', 'error')

    def has_add_permission(self, request):
        return self.model.objects.count() < 1