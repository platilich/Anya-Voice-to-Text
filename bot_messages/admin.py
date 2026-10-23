from django.contrib import admin
from .models import (StartMessages,
                     ProfileMessages,
                     SubscriptionPlusMessages,
                     LimitMessages,
                     SubscriptionStatusMessages,
                     ErrorMessages,
                     Other)


from solo.admin import SingletonModelAdmin



# Register your models here.
models = [StartMessages, ProfileMessages,
          SubscriptionPlusMessages, LimitMessages,
          SubscriptionStatusMessages, ErrorMessages,
          Other
        ]

for model in models:
    admin.site.register(model, SingletonModelAdmin)