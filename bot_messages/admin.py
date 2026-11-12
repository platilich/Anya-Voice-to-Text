from django.contrib import admin
from .models import (StartMessages,
                     ProfileMessages,
                     LimitMessages,
                     ErrorMessages,
                     Buttons,
                     ReferenceTexts)



from solo.admin import SingletonModelAdmin
from bot.logger import logger



class NativeSingletonAdmin(SingletonModelAdmin):
    change_form_template = "admin/change_form.html"
    object_history_template = "admin/object_history.html"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        logger.info(f'saved {obj.__class__.__name__} in admin')



models = [StartMessages, ProfileMessages, LimitMessages,  ErrorMessages, Buttons, ReferenceTexts]



for model in models:

    @admin.register(model)
    class SoloClass(NativeSingletonAdmin):
        pass