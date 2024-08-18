from django.db import models

class User(models.Model):
    firstName = models.CharField(max_length=32)
    lastName = models.CharField(max_length=32)
    phone = models.CharField(max_length=11)
    nationalCode = models.CharField(max_length=10)

class Otp(models.Model):
    otpCode = models.CharField(max_length=4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    createAt = models.DateTimeField(auto_now_add=True)

class Admin(models.Model):
    firstName = models.CharField(max_length=32)
    lastName = models.CharField(max_length=32)
    phone = models.CharField(max_length=11)
    nationalCode = models.CharField(max_length=10)
