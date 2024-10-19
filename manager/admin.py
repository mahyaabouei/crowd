from django.contrib import admin
from . import models


admin.site.register(models.Manager)
admin.site.register(models.Resume)
admin.site.register(models.Validation)
admin.site.register(models.Shareholder)
admin.site.register(models.History)

