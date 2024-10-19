from rest_framework import serializers
from django.contrib.auth import get_user_model
from . import models

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = '__all__'


class OtpSerializer(serializers.ModelSerializer):
    class Meta :
        model = models.Otp
        fields = '__all__'



class AdminSerializer(serializers.ModelSerializer):
    class Meta :
        model = models.Admin
        fields = '__all__'


class addressesSerializer(serializers.ModelSerializer):
    class Meta :
        model = models.addresses
        fields = '__all__'

    some_field = serializers.CharField(allow_blank=True, required=False)
    another_field = serializers.IntegerField(required=False, allow_null=True)

class accountsSerializer(serializers.ModelSerializer):
    class Meta :
        model = models.accounts
        fields = '__all__'
    some_field = serializers.CharField(allow_blank=True, required=False)
    another_field = serializers.IntegerField(required=False, allow_null=True)

class privatePersonSerializer(serializers.ModelSerializer):
    uniqueIdentifier = serializers.CharField(source='user.uniqueIdentifier', read_only=True)    
    class Meta :
        model = models.privatePerson
        fields = '__all__'
    some_field = serializers.CharField(allow_blank=True, required=False)
    another_field = serializers.IntegerField(required=False, allow_null=True)

class jobInfoSerializer(serializers.ModelSerializer):
    class Meta :
        model = models.jobInfo
        fields = '__all__'
    some_field = serializers.CharField(allow_blank=True, required=False)
    another_field = serializers.IntegerField(required=False, allow_null=True)

class tradingCodesSerializer(serializers.ModelSerializer):
    class Meta :
        model = models.tradingCodes
        fields = '__all__'
    some_field = serializers.CharField(allow_blank=True, required=False)
    another_field = serializers.IntegerField(required=False, allow_null=True)

class financialInfoSerializer(serializers.ModelSerializer):
    class Meta :
        model = models.financialInfo
        fields = '__all__'

    some_field = serializers.CharField(allow_blank=True, required=False)
    another_field = serializers.IntegerField(required=False, allow_null=True)

class legalPersonShareholdersSerializer(serializers.ModelSerializer):
    class Meta :
        model = models.legalPersonShareholders
        fields = '__all__'

    some_field = serializers.CharField(allow_blank=True, required=False)
    another_field = serializers.IntegerField(required=False, allow_null=True)

class legalPersonStakeholdersSerializer(serializers.ModelSerializer):
    class Meta :
        model = models.legalPersonStakeholders
        fields = '__all__'

    some_field = serializers.CharField(allow_blank=True, required=False)
    another_field = serializers.IntegerField(required=False, allow_null=True)

class LegalPersonSerializer(serializers.ModelSerializer):
    class Meta :
        model = models.LegalPerson
        fields = '__all__'

    some_field = serializers.CharField(allow_blank=True, required=False)
    another_field = serializers.IntegerField(required=False, allow_null=True)
