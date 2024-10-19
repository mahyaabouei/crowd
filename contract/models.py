from django.db import models
from investor.models import Cart

class SignatureCompany(models.Model) :
    name = models.CharField(max_length=150)
    national_code = models.CharField(max_length=10)
    cart = models.ForeignKey(Cart, on_delete= models.CASCADE)
    
    def __str__(self):
        return self.cart.__str__()
    



