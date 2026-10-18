from django.contrib import admin
from .models import Messages, GroqAPIKey, StickersAnya

# Register your models here.
@admin.register(Messages)
class CustomMessage(admin.ModelAdmin):
    list_display = ('hello', 'plus_ending_today', 'user_did_not_buy_subscribe')

    def has_add_permission(self, request):
        return self.model.objects.count() < 1


@admin.register(StickersAnya)
class CustomMessage(admin.ModelAdmin):
    list_display = ('hello', 'profile', 'recognising', 'limits', 'oops', 'love', 'plus')

    def has_add_permission(self, request):
        return self.model.objects.count() < 1


admin.site.register(GroqAPIKey)