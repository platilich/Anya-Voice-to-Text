from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import GroqAPIKey, Protection, DonatePrice



class NativeSingletonAdmin(SingletonModelAdmin):
    change_form_template = "admin/change_form.html"
    object_history_template = "admin/object_history.html"




@admin.register(Protection)
class Protection(NativeSingletonAdmin):
    pass


@admin.register(DonatePrice)
class SubscriptionPrice(NativeSingletonAdmin):
    pass





admin.site.register(GroqAPIKey)