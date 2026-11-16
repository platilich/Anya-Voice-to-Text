from django.contrib import admin
from .models import GeminiAPI, SelectedModels, TranscriptionMessageSettings
from solo.admin import SingletonModelAdmin
from bot.logger import logger



# Register your models here.
class NativeSingletonAdmin(SingletonModelAdmin):
    change_form_template = "admin/change_form.html"
    object_history_template = "admin/object_history.html"


    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        logger.info(f'saved {obj.__class__.__name__} in admin')



admin.site.register(GeminiAPI)


@admin.register(SelectedModels)
class SelectedModels(NativeSingletonAdmin):
    pass



@admin.register(TranscriptionMessageSettings)
class TranscriptionErrors(NativeSingletonAdmin):
    pass