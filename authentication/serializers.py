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

