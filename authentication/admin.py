from django.contrib import admin
from . import models


admin.site.register(models.User)
admin.site.register(models.Otp)
admin.site.register(models.Admin)
admin.site.register(models.tradingCodes)
admin.site.register(models.privatePerson)
admin.site.register(models.jobInfo)
admin.site.register(models.financialInfo)
admin.site.register(models.addresses)
admin.site.register(models.accounts)
admin.site.register(models.Reagent)
admin.site.register(models.LegalPerson)
admin.site.register(models.legalPersonStakeholders)
admin.site.register(models.legalPersonShareholders)