from django.db import models
from investor.models import Cart



class Manager (models.Model):
    name = models.CharField(max_length=100)
    national_id = models.CharField(max_length=100 ,  null=True , blank=True)
    national_code = models.CharField(max_length=100 ,  null=True , blank=True)
    position = models.CharField(max_length=100,  null=True , blank=True)
    is_legal = models.BooleanField(default=False,  null=True , blank=True) #حقوقی
    phone = models.CharField(max_length=14,  null=True , blank=True)
    is_obliged = models.BooleanField(default=False,  null=True , blank=True) #موظف
    representative = models.CharField(max_length=100,  null=True , blank=True)
    cart = models.ForeignKey(Cart,  on_delete=models.CASCADE)
    signature = models.BooleanField(default=False)
    lock = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)
    

    
class Resume (models.Model):
    file = models.FileField(upload_to='static/')
    manager = models.ForeignKey(Manager,  on_delete=models.CASCADE)
    lock = models.BooleanField(default=False)

    def __str__(self):
        return str(self.manager.name)
    


class Shareholder (models.Model):
    name = models.CharField(max_length=100)
    national_code = models.CharField(max_length=50, null=True, blank=True)
    national_id = models.CharField(max_length=50, null=True, blank=True)
    percent = models.CharField(max_length=99999999 , null=True, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    lock = models.BooleanField(default=False)
    phone = models.CharField(max_length=14)

    def __str__(self):
        return self.name


class Validation (models.Model) :
    file_manager = models.FileField(upload_to ='static/')
    manager = models.CharField(max_length=14)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    lock = models.BooleanField(default=False)
    date = models.DateTimeField(blank=True, null=True) 

    def __str__(self):
        return  f"Validation for Cart ID: {self.cart.id}"



class History (models.Model) :
    file = models.FileField(upload_to  ='static/')
    manager = models.ForeignKey(Manager,  on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    lock = models.BooleanField(default=False)
    date = models.DateTimeField(blank=True, null=True) 
    def __str__(self):
        return  f"{self.cart} - {self.lock}"

