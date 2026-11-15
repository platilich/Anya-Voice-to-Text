from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import Protection



class NativeSingletonAdmin(SingletonModelAdmin):
    change_form_template = "admin/change_form.html"
    object_history_template = "admin/object_history.html"




@admin.register(Protection)
class Protection(NativeSingletonAdmin):
    pass