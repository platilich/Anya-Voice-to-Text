from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import GroqAPIKey, StickersAnya, Protection, SubscriptionPrice, SummarizeButtonSettings, CommandGetProStatus





class NativeSingletonAdmin(SingletonModelAdmin):
    change_form_template = "admin/change_form.html"
    object_history_template = "admin/object_history.html"




for i in [StickersAnya, Protection, SubscriptionPrice, SummarizeButtonSettings, CommandGetProStatus]:
    @admin.register(i)
    class i(NativeSingletonAdmin):
        pass



admin.site.register(GroqAPIKey)