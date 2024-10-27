from django.shortcuts import render
import datetime
from . import serializers
from .models import Wallet , Transaction 
from rest_framework import status 
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication import fun
from django.http import HttpResponse, HttpResponseNotAllowed
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit   
from django.utils.decorators import method_decorator



# done
class WalletAdminViewset(APIView):
    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get (self,request):
        Authorization = request.headers.get('Authorization')     
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()

        wallet = Wallet.objects.all()
        if not wallet :
            return Response({'error': 'wallet not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.WalletSerializer(wallet , many = True)
        if serializer:
            return Response({'wallet': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# done
class WalletAdmin2Viewset(APIView):
    @method_decorator(ratelimit(key='ip', rate='5/m', method='PATCH', block=True))
    def patch (self,request,id) :
        Authorization = request.headers.get('Authorization')     
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()

        wallet =  Wallet.objects.filter(id=id).first()
        if not wallet :
            return Response({'error': 'wallet not found'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data.copy()
        serializer = serializers.WalletSerializer(wallet , data = data , partial = True) 
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'wallet updated successfully', 'wallet': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get (self,request,id) :
        Authorization = request.headers.get('Authorization')     
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()

        wallet = Wallet.objects.filter(id=id).first()
        if not wallet :
            return Response({'error': 'wallet not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.WalletSerializer(wallet)
        if serializer :
            return Response({'wallet': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 

# done
class WalletViewset(APIView) :
    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get (self,request) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()   
        wallet = Wallet.objects.filter(user=user).first()
        serializer = serializers.WalletSerializer(wallet)
        if serializer :
            return Response({'wallet': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# done
class TransactionAdminViewset(APIView):
    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get(self,request) :
        Authorization = request.headers.get('Authorization')     
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()

        transaction = Transaction.objects.all()
        if not transaction :
            return Response({'error': 'transaction not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.TransactionSerializer(transaction , many = True)
        if serializer:
            return Response({'transaction': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  


# done
class TransactionAdmin2Viewset(APIView):
    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get(self,request,id) :
        Authorization = request.headers.get('Authorization')     
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()

        transaction = Transaction.objects.filter(id=id).first()
        if not transaction :
            return Response({'error': 'transaction not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.TransactionSerializer(transaction )
        if serializer:
            return Response({'transaction': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  


    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def patch (self,request,id) :
        Authorization = request.headers.get('Authorization')     
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()

        transaction =  Transaction.objects.filter(id=id).first()
        if not transaction :
            return Response({'error': 'transaction not found'}, status=status.HTTP_404_NOT_FOUND)
        wallet = Wallet.objects.filter(user=transaction.wallet.user).first()

        data = request.data.get('status')
        update_data = {'status': data }

        if data == True :
            credit_amount = transaction.credit_amount
            remaining = wallet.remaining
            remaining_amount = str(credit_amount + remaining)
            wallet.remaining =remaining_amount 
            wallet.save()
            serializer = serializers.TransactionSerializer(transaction, data=update_data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'The amount was added to the wallet', 'transaction': serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        if data != True :
            credit_amount = transaction.credit_amount
            remaining = wallet.remaining
            remaining_amount = str(remaining - credit_amount)
            wallet.remaining =remaining_amount 
            wallet.save()
            serializer = serializers.TransactionSerializer(transaction, data=update_data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'The amount was deducted from the wallet', 'transaction': serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if data is None:
            return Response({'error': 'status field is missing'}, status=status.HTTP_400_BAD_REQUEST)

   
# done
class TransactionViewset(APIView) :
    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get (self,request) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()
        wallet = Wallet.objects.filter(user=user).first()
        transaction = Transaction.objects.filter(wallet=wallet)
        serializer = serializers.TransactionSerializer(transaction , many=True)
        if serializer :
            return Response({'transaction': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post (self, request) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()
        wallet = Wallet.objects.filter(user=user).first()
        if not wallet:
            return Response({'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not request.FILES.get('image_receipt' , 'document_number'):
            return Response({'error': 'هیچی نیست'}, status=status.HTTP_400_BAD_REQUEST)
        image_receipt = request.FILES['image_receipt']
        
        transaction = Transaction.objects.create (
            wallet = wallet , 
            method = '2' , 
            description_transaction  ='واریز فیش بانکی' , 
            image_receipt = image_receipt , 
            document_number = request.data['document_number'] ,
            credit_amount = request.data['credit_amount'] , 
            debt_amount = 0
            )
        
        serializer = serializers.TransactionSerializer(transaction)
        return Response ({'transaction' : serializer.data } ,  status=status.HTTP_200_OK)
    

# done
class Transaction2Viewset(APIView):
    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get (self,request,id) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()  
        wallet = Wallet.objects.filter(user=user).first()
        transaction = Transaction.objects.filter(id=id , wallet=wallet).first()
        if transaction is None :
            return Response({'error': 'Transaction not found for this user'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.TransactionSerializer(transaction)
        if serializer :
            return Response({'transaction': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

