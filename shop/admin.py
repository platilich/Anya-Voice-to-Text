from django.contrib import admin
from solo.admin import SingletonModelAdmin
from bot.logger import logger
from .models import ShopTexts, ShopMinutePrice, ShopStatus


# Register your models here.
class NativeSingletonAdmin(SingletonModelAdmin):
    change_form_template = "admin/change_form.html"
    object_history_template = "admin/object_history.html"


    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        logger.info(f'saved {obj.__class__.__name__} in admin')




@admin.register(ShopTexts)
class ShopTexts(NativeSingletonAdmin):
    pass


@admin.register(ShopMinutePrice)
class ShopMinutePrice(NativeSingletonAdmin):
    pass


@admin.register(ShopStatus)
class ShopStatus(NativeSingletonAdmin):
    pass
