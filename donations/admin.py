from django.contrib import admin
from solo.admin import SingletonModelAdmin
from bot.logger import logger
from .models import DonatePrice, DonationMessages


# Register your models here.
class NativeSingletonAdmin(SingletonModelAdmin):
    change_form_template = "admin/change_form.html"
    object_history_template = "admin/object_history.html"


    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        logger.info(f'saved {obj.__class__.__name__} in admin')




@admin.register(DonatePrice)
class DonationPrice(NativeSingletonAdmin):
    pass


@admin.register(DonationMessages)
class DonationMessages(NativeSingletonAdmin):
    pass