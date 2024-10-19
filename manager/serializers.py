from rest_framework import serializers
from django.contrib.auth import get_user_model
from . import models
from investor.serializers import CartSerializer




class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Manager
        fields = '__all__'



class CartWithManagersSerializer(serializers.ModelSerializer):
    managers = ManagerSerializer(many=True, read_only=True, source='manager_set')

    class Meta:
        model = models.Cart
        fields = '__all__'


class ShareholderSerializer (serializers.ModelSerializer):
    class Meta:
        model = models.Shareholder
        fields = '__all__'


class CartWithShareholderSerializer(serializers.ModelSerializer):
    shareholder = ShareholderSerializer(many=True, read_only=True, source='shareholder_set')
    class Meta:
        model = models.Cart
        fields = '__all__'

class ResumeSerializer (serializers.ModelSerializer):
    class Meta:
        model = models.Resume
        fields = ['file', 'manager' , 'lock']
    # def create(self, validated_data):
    #         manager = validated_data.get('manager')
    #         file = validated_data.get('file')
    #         resume = models.Resume.objects.create(manager=manager, file=file)
    #         return resume

class ValidationSerializer (serializers.ModelSerializer):
    class Meta:
        model = models.Validation
        fields = ['manager' , 'cart'  , 'file_manager' , 'lock' , 'date']


class HistorySerializer (serializers.ModelSerializer):
    class Meta:
        model = models.History
        fields = ['id', 'file', 'lock', 'date', 'manager', 'cart']

