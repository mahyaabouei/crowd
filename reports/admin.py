from django.contrib import admin
from . import models


admin.site.register(models.ProgressReport)
admin.site.register(models.AuditReport)
