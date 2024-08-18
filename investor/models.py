from django.db import models

#  کارت درخواست سرمایه پذیر
class Cart (models.Model) :
    company_name = models.CharField(max_length=200)
    activity_industry = models.CharField(max_length=200)
    registration_number = models.IntegerField(unique=True)
    national_id = models.IntegerField(unique=True)
    registered_capital = models.IntegerField()
    personnel = models.IntegerField()
    OPTION_KIND = [
        ('special stock', 'special stock'),
        ('common stock', 'common stock'),
    ]
    company_kind = models.CharField(max_length=10, choices=OPTION_KIND)
    amount_of_request = models.IntegerField ()



    def __str__(self):
        return self.company_name