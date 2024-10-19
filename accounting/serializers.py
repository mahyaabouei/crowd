from rest_framework import serializers
from . import models


class WalletSerializer (serializers.ModelSerializer):
    uniqueIdentifier = serializers.CharField(source='user.uniqueIdentifier', read_only=True)    
    class Meta:
        model = models.Wallet
        fields = '__all__'

        
class TransactionSerializer (serializers.ModelSerializer):
    class Meta:
        model = models.Transaction
        fields = '__all__'
