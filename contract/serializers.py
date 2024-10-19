from rest_framework import serializers
from . import models



class SignatureCompanySerializer (serializers.ModelSerializer):
    class Meta :
        model = models.SignatureCompany
        fields = ['name', 'national_code', 'cart']