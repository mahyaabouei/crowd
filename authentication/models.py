from django.db import models

class User(models.Model):
    firstName = models.CharField(max_length=32)
    lastName = models.CharField(max_length=32)
    mobile = models.CharField(max_length=11)
    national_code = models.CharField(max_length=10)

    def __str__(self):
        national_code = self.national_code if self.national_code else "NoNationalCode"
        return f'{national_code}'
    
class Otp(models.Model):
    code = models.CharField(max_length=4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=11)
    date = models.DateTimeField(auto_now_add=True)

class Admin(models.Model):
    firstName = models.CharField(max_length=32)
    lastName = models.CharField(max_length=32)
    mobile = models.CharField(max_length=11)
    nationalCode = models.CharField(max_length=10)
