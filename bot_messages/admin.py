from django.contrib import admin
from .models import (StartMessages,
                     ProfileMessages,
                     SubscriptionPlusMessages,
                     LimitMessages,
                     SubscriptionStatusMessages,
                     ErrorMessages,
                     Other)



from solo.admin import SingletonModelAdmin



class NativeSingletonAdmin(SingletonModelAdmin):
    change_form_template = "admin/change_form.html"
    object_history_template = "admin/object_history.html"



models = [StartMessages, ProfileMessages,
          SubscriptionPlusMessages, LimitMessages,
          SubscriptionStatusMessages, ErrorMessages,
          Other
        ]



for model in models:

    @admin.register(model)
    class StickerAnyaAdmin(NativeSingletonAdmin):
        pass