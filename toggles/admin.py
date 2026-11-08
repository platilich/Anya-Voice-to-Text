from django.contrib import admin
from .models import SummarizeButtonSettings, CommandGetProStatus
from solo.admin import SingletonModelAdmin


class NativeSingletonAdmin(SingletonModelAdmin):
    change_form_template = "admin/change_form.html"
    object_history_template = "admin/object_history.html"



# Register your models here.
@admin.register(SummarizeButtonSettings)
class SummarizeButtonSettings(NativeSingletonAdmin):
    pass



@admin.register(CommandGetProStatus)
class CommandGetProStatus(NativeSingletonAdmin):
    pass