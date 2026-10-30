from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import GroqAPIKey, StickersAnya, Protection, SubscriptionPrice, SummarizeButtonSettings





class NativeSingletonAdmin(SingletonModelAdmin):
    change_form_template = "admin/change_form.html"
    object_history_template = "admin/object_history.html"




for element in [StickersAnya, Protection, SubscriptionPrice, SummarizeButtonSettings]:
    @admin.register(element)
    class element(NativeSingletonAdmin):
        pass



admin.site.register(GroqAPIKey)