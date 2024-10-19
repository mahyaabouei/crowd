from django.contrib import admin
from . import models


admin.site.register(models.Cart)
admin.site.register(models.Message)
# admin.site.register(models.SetStatus)
admin.site.register(models.AddInformation)


