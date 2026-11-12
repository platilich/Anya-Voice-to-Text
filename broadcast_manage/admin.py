from django.contrib import admin
from .models import BroadcastTexts, BroadcastTime, BroadcastStatus
from bot.logger import logger
from solo.admin import SingletonModelAdmin


# Register your models here.
class NativeSingletonAdmin(SingletonModelAdmin):
    change_form_template = "admin/change_form.html"
    object_history_template = "admin/object_history.html"


    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        logger.info(f'saved {obj.__class__.__name__} in admin')




@admin.register(BroadcastTime)
class BroadcastTime(NativeSingletonAdmin):
    pass


@admin.register(BroadcastTexts)
class BroadcastTexts(NativeSingletonAdmin):
    pass


@admin.register(BroadcastStatus)
class BroadcastStatus(NativeSingletonAdmin):
    pass
