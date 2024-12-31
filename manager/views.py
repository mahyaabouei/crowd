from .models import Manager ,  Resume , Validation , Shareholder , History
from rest_framework.response import Response
from rest_framework import status 
from rest_framework.views import APIView
from authentication import fun
from . import serializers
from investor import models
import datetime
from django.utils import timezone
from investor.time import get_date_from_request
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit   
from django.utils.decorators import method_decorator
from crowd import settings



# done
class ManagerViewset(APIView) :
    @method_decorator(ratelimit(**settings.RATE_LIMIT['POST']), name='post')
    def post (self , request , unique_id ):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_401_UNAUTHORIZED)
        user = user.first()
        cart = models.Cart.objects.filter(unique_id=unique_id).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        manager = Manager.objects.filter(cart=cart)
        if manager :
            manager.delete()
        managers_data = request.data.get('managers', [])
        for manager_data in managers_data:
            serializer = serializers.ManagerSerializer(data={**manager_data, 'cart': cart.id})
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(cart=cart)
        serializer = serializers.CartWithManagersSerializer(cart)
        return Response({'message': True, 'data': serializer.data}, status=status.HTTP_200_OK)
    
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get (self,request , unique_id):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_401_UNAUTHORIZED)
        user = user.first()
        cart = models.Cart.objects.filter(unique_id=unique_id).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        
        managers = Manager.objects.filter(cart=cart)
        serializer = serializers.ManagerSerializer(managers, many=True)
        return Response({'message': True, 'data': serializer.data}, status=status.HTTP_200_OK)
    

# done
class ManagerAdminViewset(APIView):
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get (self,request,unique_id):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        cart = models.Cart.objects.filter(unique_id=unique_id).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        
        managers = Manager.objects.filter(cart=cart)
        serializer = serializers.ManagerSerializer(managers, many=True)
        return Response({'message': True ,  'data': serializer.data }, status=status.HTTP_200_OK)
    @method_decorator(ratelimit(**settings.RATE_LIMIT['POST']), name='post')
    def post(self, request, unique_id):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)

        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()

        if unique_id is None:
            return Response({'error': 'Cart unique_id is missing'}, status=status.HTTP_400_BAD_REQUEST)

        cart = models.Cart.objects.filter(unique_id=unique_id).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        managers_data = request.data.get('managers', [])
        updated_managers = []  
        
        for manager_data in managers_data:
            national_code = manager_data.get('national_code')
            if not national_code:
                return Response({'error': 'Manager national_code is missing'}, status=status.HTTP_400_BAD_REQUEST)

            manager = Manager.objects.filter(national_code=national_code, cart=cart).first()

            if manager:
                serializer = serializers.ManagerSerializer(manager, data=manager_data, partial=True)
                if not serializer.is_valid():
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                serializer.save()
                updated_managers.append(serializer.instance)  
            else:
                serializer = serializers.ManagerSerializer(data={**manager_data, 'cart': cart.id})
                if not serializer.is_valid():
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                serializer.save(cart=cart)
                updated_managers.append(serializer.instance)  

        serializer = serializers.ManagerSerializer(updated_managers, many=True)
        
        return Response({'message': True, 'data': serializer.data}, status=status.HTTP_200_OK)


# done
class ResumeViewset(APIView):
    @method_decorator(ratelimit(**settings.RATE_LIMIT['POST']), name='post')
    def post (self,request,unique_id) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_401_UNAUTHORIZED)
        user = user.first()
        
        cart = models.Cart.objects.filter(unique_id=unique_id).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        
        for file_key, file_value in request.FILES.items():
            manager = Manager.objects.filter(national_code=file_key, cart=cart).first()
            if not manager:
                return Response({'error': 'Management not found'}, status=status.HTTP_404_NOT_FOUND)

            resume = Resume.objects.filter(manager=manager)
            if resume:
                resume.delete()

            data = {
                'file': file_value,
                'manager': manager.id,
                
            }
            serializer = serializers.ResumeSerializer(data = data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()        
        return Response({'success' : True}, status=status.HTTP_200_OK)

    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get (self,request,unique_id) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_401_UNAUTHORIZED)
        user = user.first()
        cart = models.Cart.objects.filter(user=user,unique_id=unique_id)
        if not cart.exists():
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        cart = cart.first()
        manager = Manager.objects.filter(cart=cart)
        if not manager.exists():
            return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)
        resume_list = []
        for i in manager:
            resume = Resume.objects.filter(manager=i)
            national_code = i.national_code
            name = i.name
            lock = False
            file = None
            if resume.exists():
              resume = resume.first()
              resume = serializers.ResumeSerializer(resume).data
              lock = resume['lock']
              file = resume['file']
              
              
            resume_list.append({'national_code': national_code,'lock': lock,'file': file,'name':name})

        return Response({'manager': resume_list}, status=status.HTTP_200_OK)


# done
class ResumeAdminViewset(APIView) :
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get(self, request,unique_id) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        cart = models.Cart.objects.filter(unique_id=unique_id)
        if not cart.exists():
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        cart = cart.first()
        manager = Manager.objects.filter(cart=cart)
        if not manager.exists():
            return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)
        resume_list = []
        for i in manager:
            resume = Resume.objects.filter(manager=i)
            national_code = i.national_code
            name = i.name
            lock = False
            file = None
            if resume.exists():
              resume = resume.first()
              resume = serializers.ResumeSerializer(resume).data
              lock = resume['lock']
              file = resume['file']
              
              
            resume_list.append({'national_code': national_code,'lock': lock,'file': file,'name':name})

        return Response({'manager': resume_list}, status=status.HTTP_200_OK)
    @method_decorator(ratelimit(**settings.RATE_LIMIT['POST']), name='post')
    def post(self, request, unique_id):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        managers_data = []

        data = request.data.copy()
        cart = models.Cart.objects.filter(unique_id=unique_id)
        if len(cart) == 0:
            return Response({'error': 'Not found cart'}, status=status.HTTP_400_BAD_REQUEST)
        cart = cart.first()


        if request.FILES:
            for file_key, file in request.FILES.items():
                lock = False
                manager = Manager.objects.filter(national_code=file_key, cart=cart)
                if not manager:
                    return Response({'error': 'Not found management for national_code {file_key}'}, status=status.HTTP_400_BAD_REQUEST)
                manager = manager.first()
                existing_resumes = Resume.objects.filter(manager=manager)
                if existing_resumes.exists():
                    existing_resumes.delete()
                resume = Resume(file=file, manager=manager, lock=lock)
                resume.save()
                serializer = serializers.ResumeSerializer(resume)
                # managers_data.append(serializer.data)
        for lock_key in request.data.copy():

            if 'lock' in lock_key:
                _key = lock_key.split('_')[0]
                manager = Manager.objects.filter(national_code=_key, cart=cart)
                if not manager :
                    return Response({'error': f'Not found management for national_code {file_key}'}, status=status.HTTP_400_BAD_REQUEST)
                manager = manager.first()
                resumes = Resume.objects.filter(manager=manager).first()
                try :
                    resumes.lock = request.data.copy()[lock_key] == 'true'
                    resumes.save()
                    managers_data.append(serializer.data)
                except :
                    pass
            else:
                manager = Manager.objects.filter(national_code=lock_key, cart=cart)
                if manager.exists() :
                    manager = manager.first()
                    resumes = Resume.objects.filter(manager=manager)
                    if request.data.get(lock_key) in ['null', 'undefined', None, '']:
                        resumes = resumes.first()
                        resumes.delete()



        return Response({'managers': managers_data }, status=status.HTTP_201_CREATED)


# done
class ShareholderViewset(APIView):
    @method_decorator(ratelimit(**settings.RATE_LIMIT['POST']), name='post')
    def post(self, request,unique_id):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_401_UNAUTHORIZED)
        user = user.first()
        cart = models.Cart.objects.filter(unique_id=unique_id).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        shareholder = Shareholder.objects.filter(cart=cart)
        if shareholder :
            shareholder.delete()

        shareholder  = request.data.get('shareholder', [])
        all_serialized = [] 

        for shareholder in shareholder:
            serializer = serializers.ShareholderSerializer(data={**shareholder, 'cart': cart.id})
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(cart=cart)
            all_serialized.append(serializer.data)  # اضافه کردن داده‌های سریالایز شده به لیست

        return Response({'message': True, 'data': all_serialized}, status=status.HTTP_200_OK)



    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get (self, request , unique_id) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_401_UNAUTHORIZED)
        user = user.first()
        cart = models.Cart.objects.filter(unique_id=unique_id).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        
        shareholder = Shareholder.objects.filter(cart=cart)
        serializer = serializers.ShareholderSerializer(shareholder, many=True)
        return Response({'message': True, 'data': serializer.data}, status=status.HTTP_200_OK)


# done
class ShareholderAdminViewset(APIView) :
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get (self, request, unique_id) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        cart = models.Cart.objects.filter(unique_id=unique_id).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        
        shareholder = Shareholder.objects.filter(cart=cart)
        serializer = serializers.ShareholderSerializer(shareholder, many=True)
        return Response({'message': True ,  'data': serializer.data }, status=status.HTTP_200_OK)

    @method_decorator(ratelimit(**settings.RATE_LIMIT['POST']), name='post')
    def post(self,request,unique_id) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        if unique_id is None:
            return Response({'error': 'Manager ID is missing'}, status=status.HTTP_400_BAD_REQUEST)
        cart = models.Cart.objects.filter(unique_id=unique_id).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        shareholder = Shareholder.objects.filter(cart=cart)
        if shareholder :
            shareholder.delete()
  
        shareholder  = request.data.get('shareholder', [])
        all_serialized = [] 
        for shareholder in shareholder:

            serializer = serializers.ShareholderSerializer(data={**shareholder, 'cart': cart.id})
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(cart=cart)
            all_serialized.append(serializer.data)   
    
        return Response({'message': True, 'data': all_serialized}, status=status.HTTP_200_OK)


# done
class ValidationViewset (APIView) :
    @method_decorator(ratelimit(**settings.RATE_LIMIT['POST']), name='post')
    def post(self, request, unique_id):
        try:
            Authorization = request.headers.get('Authorization')
            if not Authorization:
                return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = fun.decryptionUser(Authorization)
            if not user:
                return Response({'error': 'user not found'}, status=status.HTTP_401_UNAUTHORIZED)
            
            user = user.first()
            cart = models.Cart.objects.filter(unique_id=unique_id).first()
            if not cart:
                return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

            validation_existing = Validation.objects.filter(cart=cart, manager='1').first()

            file_manager = request.FILES.get('1')
            date_manager = request.data.copy()

            if not file_manager and not validation_existing:
                return Response({'error': 'File validation is missing'}, status=status.HTTP_400_BAD_REQUEST)

            manager_list = []

            for national_code, file in request.FILES.items():
                if national_code == '1':
                    continue

                manager = Manager.objects.filter(national_code=national_code, cart=cart).first()
                if not manager:
                    return Response({'error': f'Manager with national code {national_code} not found for this cart'}, status=status.HTTP_404_NOT_FOUND)

                existing_validation = Validation.objects.filter(manager=manager.national_code, cart=cart).first()
                if existing_validation:
                    existing_validation.file_manager.delete()
                    existing_validation.delete()
                date = int(date_manager[f'{national_code}_date'])/1000
                date = datetime.datetime.fromtimestamp(date)

                new_validation = Validation.objects.create(file_manager=file, manager=manager.national_code, cart=cart, date=date)
                new_validation.save()

                manager_list.append({
                    'national_code': manager.national_code,
                    'name': manager.name,
                    'file_manager': new_validation.file_manager.url if new_validation.file_manager else None,
                    'date' : new_validation.date
                })

            if file_manager:
                if validation_existing:
                    validation_existing.file_manager.delete()
                    validation_existing.delete()
                date = int(date_manager['1_date'])/1000
                date = datetime.datetime.fromtimestamp(date)
                validation = Validation.objects.create(file_manager=file_manager, cart=cart, manager='1',date=date)
                validation.save()

                manager_list.append({
                    'national_code': '1',
                    'name': 'شرکت',
                    'file_manager': validation.file_manager.url if validation.file_manager else None,
                    'date' : validation.date
                })
            else:
                manager_list.append({
                    'national_code': '1',
                    'name': 'شرکت',
                    'file_manager': validation_existing.file_manager.url if validation_existing and validation_existing.file_manager else None , 
                    'date' : validation.date
                })

            response_data = {
                'managers': manager_list
            }

            return Response({'data': response_data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get(self, request, unique_id):
        try:
            Authorization = request.headers.get('Authorization')
            if not Authorization:
                return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = fun.decryptionUser(Authorization)
            if not user:
                return Response({'error': 'user not found'}, status=status.HTTP_401_UNAUTHORIZED)
            
            user = user.first()
            cart = models.Cart.objects.filter(unique_id=unique_id).first()
            if not cart:
                return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

            managers = Manager.objects.filter(cart=cart)
            if not managers.exists():
                return Response({'error': 'No managers found for this cart'}, status=status.HTTP_404_NOT_FOUND)

            manager_list = []
            for manager in managers:
                validation = Validation.objects.filter(manager=manager.national_code, cart=cart).first()
                

                if validation:
                    date = validation.date
                else:
                    date = datetime.datetime.now()

                

                manager_list.append({
                    'national_code': manager.national_code,
                    'name': manager.name,
                    'file_manager': validation.file_manager.url if validation and validation.file_manager else None,
                    'date' : date
                })


            company_validation = Validation.objects.filter(manager='1', cart=cart).first()

            if company_validation:
                date = company_validation.date
            else:
                date = datetime.datetime.now()

            manager_list.append({
                'national_code': '1',
                'name': 'شرکت',
                'file_manager': company_validation.file_manager.url if company_validation and company_validation.file_manager else None,
                'date' : date

            })

            response_data = {
                'managers': manager_list
            }

            return Response({'data': response_data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# done
class ValidationAdminViewset (APIView) :
    @method_decorator(ratelimit(**settings.RATE_LIMIT['POST']), name='post')
    def post (self, request, unique_id) :
        try :
            Authorization = request.headers.get('Authorization')
            if not Authorization:
                return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
            admin = fun.decryptionadmin(Authorization)
            if not admin:
                return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
            admin = admin.first()
            cart = models.Cart.objects.filter(unique_id=unique_id).first()
            if not cart:
                return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

            file_manager = request.FILES.get('1')
            date_manager = request.data.copy()
            validation_existing = Validation.objects.filter(cart=cart, manager='1' ).first()
            if not file_manager and not validation_existing:
                 validation_existing.file_manager.delete()
                 validation_existing.delete()
            elif not file_manager and not validation_existing:
                 return Response({'error': 'File validation is missing'}, status=status.HTTP_400_BAD_REQUEST)

            manager_list = []
            for national_code, file in request.FILES.items():
                if national_code == '1':
                    continue
                lock_key = f'lock_{national_code}'
                lock = request.data.get(lock_key, 'false').lower() == 'true'

                manager = Manager.objects.filter(national_code=national_code, cart=cart).first()
                if not manager:
                    return Response({'error': f'Manager with national code {national_code} not found for this cart'}, status=status.HTTP_404_NOT_FOUND)

                existing_validation = Validation.objects.filter(manager=manager.national_code, cart=cart , lock = lock).first()
                if existing_validation:
                    existing_validation.file_manager.delete()

                    existing_validation.delete()
                date = int(date_manager[f'{national_code}_date'])/1000
                date = datetime.datetime.fromtimestamp(date)
                new_validation = Validation.objects.create(file_manager=file, manager=manager.national_code, cart=cart, date=date , lock = lock)

                new_validation.save()

                manager_list.append({
                    'national_code': manager.national_code,
                    'name': manager.name,
                    'file_manager': new_validation.file_manager.url if new_validation.file_manager else None,
                    'date' : new_validation.date,
                    'lock' : lock
                })
            for i in request.data.copy():
                if i not in ['lock_1','1_date']:
                    if 'lock' in i:
                        national_code = i.split('_')[1]
                        validation = Validation.objects.filter(manager=national_code).first()
                        validation.lock = request.data.get(i, 'false').lower() == 'true'
                        validation.save()

                    if 'date' in i:
                        national_code = i.split('_')[0]
                        validation = Validation.objects.filter(manager=national_code).first()
                        date = int(request.data.get(i))/1000
                        date = datetime.datetime.fromtimestamp(date)
                        validation.date = date
                        validation.save()

                key = i
            if file_manager:
                lock_company = request.data.get('lock_1', 'false').lower() == 'true'
                if validation_existing:
                    validation_existing.file_manager.delete()
                    validation_existing.delete()
                date = int(date_manager['1_date'])/1000
                date = datetime.datetime.fromtimestamp(date)
                validation = Validation.objects.create(file_manager=file_manager, cart=cart, manager='1',date=date ,  lock=lock)
                validation.save()

                manager_list.append({
                    'national_code': '1',
                    'name': 'شرکت',
                    'file_manager': validation.file_manager.url if validation.file_manager else None,
                    'date' : validation.date,
                    'lock' : lock_company

                })
            else:
                date_comp = int(int(date_manager['1_date'])/1000)
                date_comp = datetime.datetime.fromtimestamp(date_comp)
                validation_existing.date = str(date_comp)
                validation_existing.lock = request.data.get('lock_1', 'false').lower() == 'true'
                validation_existing.save()
                manager_list.append({
                    'national_code': '1',
                    'name': 'شرکت',
                    'file_manager': validation_existing.file_manager.url if validation_existing and validation_existing.file_manager else None,
                    'date' : validation_existing.date,
                    'lock' : validation_existing.lock if validation_existing else False
                })
            response_data = {
                'managers': manager_list
            }

            return Response({'data': response_data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get (self, request, unique_id) :
        try :
            Authorization = request.headers.get('Authorization')
            if not Authorization:
                return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
            admin = fun.decryptionadmin(Authorization)
            if not admin:
                return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
            admin = admin.first()
            cart = models.Cart.objects.filter(unique_id=unique_id).first()
            if not cart:
                return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

            managers = Manager.objects.filter(cart=cart)
            if not managers.exists():
                return Response({'error': 'No managers found for this cart'}, status=status.HTTP_404_NOT_FOUND)

            manager_list = []
            for manager in managers:
                validation = Validation.objects.filter(manager=manager.national_code, cart=cart).first()
                if validation:
                  date = validation.date
                else:
                    date = datetime.datetime.now()


                manager_list.append({
                    'national_code': manager.national_code,
                    'name': manager.name,
                    'file_manager': validation.file_manager.url if validation and validation.file_manager else None,
                    'date' : str(date),
                    'lock' : validation.lock if validation and validation.lock else None
                })

            company_validation = Validation.objects.filter(manager='1', cart=cart).first()
            if company_validation :
                date = company_validation.date
            else:
                date = datetime.datetime.now()
            manager_list.append({
                'national_code': '1',
                'name': 'شرکت',
                'file_manager': company_validation.file_manager.url if company_validation and company_validation.file_manager else None,
                'date' : str(date),
                'lock' : company_validation.lock if company_validation else None

            })

            response_data = {
                'managers': manager_list
            }

            return Response({'data': response_data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# done
class HistoryViewset (APIView) :
    @method_decorator(ratelimit(**settings.RATE_LIMIT['POST']), name='post')
    def post (self, request, unique_id) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_401_UNAUTHORIZED)
        user = user.first()
        cart = models.Cart.objects.filter(unique_id=unique_id).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        if not request.FILES:
            return Response({'error': 'No files were uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        date_manager = request.data.copy()
        manager_list = []

        for file_key, file_value in request.FILES.items():
            manager = Manager.objects.filter(national_code=file_key, cart=cart).first()
            if not manager:
                return Response({'error': f'Manager with national code {file_key} not found for this cart'}, status=status.HTTP_404_NOT_FOUND)
            try:
                timestamp_key = f'{manager.national_code}_date'  
                if timestamp_key not in date_manager:
                    return Response({'error': f'Date for manager with national code {manager.national_code} is missing'}, status=status.HTTP_400_BAD_REQUEST)
                
                date = int(date_manager[timestamp_key]) / 1000  
                date = datetime.datetime.fromtimestamp(date)     

            except (KeyError, ValueError) as e:
                return Response({'error': f'Invalid date format for manager {manager.national_code}'}, status=status.HTTP_400_BAD_REQUEST)
            
            existing_history = History.objects.filter(manager=manager, cart=cart).first()
            
            if existing_history:
                existing_history.delete()  
            new_history = History.objects.create(file=file_value, manager=manager, cart=cart , date=date)

            manager_list.append({
                'national_code': manager.national_code,
                'name': manager.name,
                'file': new_history.file.url if new_history.file else None,
                'date' : new_history.date
            })
        return Response({'managers': manager_list}, status=status.HTTP_200_OK)



    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get (self, request, unique_id) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response ({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response ({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()
        cart = models.Cart.objects.filter(unique_id=unique_id).first()
        if not cart:
            return Response ({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        manager = Manager.objects.filter(cart=cart)
        if not manager.exists():
            return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)
        manager_list = []
        for i in manager:
            history = History.objects.filter(manager=i).first()
            
            if history:
                date = history.date 
            else:
                date = datetime.datetime.now()
                
            national_code = i.national_code
            name = i.name
            lock = False
            file = None

            
            if history:
                history = serializers.HistorySerializer(history).data
                lock = history['lock']
                file = history['file']
                date = history ['date']

   
            manager_list.append({
                'national_code': national_code,
                'lock': lock,
                'file': file,
                'name': name ,
                'date' : date 
            })

        return Response({'manager': manager_list}, status=status.HTTP_200_OK)


# done
class HistoryAdminViewset (APIView) :
    @method_decorator(ratelimit(**settings.RATE_LIMIT['POST']), name='post')
    def post(self, request, unique_id):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        
        cart = models.Cart.objects.filter(unique_id=unique_id).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if request.FILES:
            for file_key, file in request.FILES.items():
                lock = False
                manager = Manager.objects.filter(national_code=file_key, cart=cart)
                if not manager.exists():
                    return Response({'error': f'Not found management for national_code {file_key}'}, status=status.HTTP_400_BAD_REQUEST)
                manager = manager.first()

                history = History.objects.filter(manager=manager).first()
                if history :
                    history.delete()
                if history is None:
                    date, error_message = get_date_from_request(request, manager.national_code)
                    if error_message:
                        return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
                    
                    history = History(file=file, manager=manager, lock=lock, cart=cart, date=date)
                    history.save()
                

                

        
        for lock_key in request.data:
            if 'lock' in lock_key:
                _key = lock_key.split('_')[1]
                manager = Manager.objects.filter(national_code=_key, cart=cart)
                if not manager.exists():
                    return Response({'error': f'Not found management for national_code {_key}'}, status=status.HTTP_400_BAD_REQUEST)
                manager = manager.first()

                date, error_message = get_date_from_request(request, _key)
                if error_message:
                    return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
            
                history = History.objects.filter(manager=manager, date=date).first()
                
                if history:
                    if lock_key in request.data:
                        history.lock = request.data[lock_key].lower() == 'true'  
                        history.save()
                        history.refresh_from_db()
                        serializer = serializers.HistorySerializer(history)

                    else:
                        return Response({'error': f'Lock status for manager {manager.national_code} is missing'}, status=status.HTTP_400_BAD_REQUEST)
        managers_data = History.objects.filter(cart=cart)
        serializer = serializers.HistorySerializer(managers_data,many=True)
        return Response({'managers': serializer.data}, status=status.HTTP_200_OK)
      

    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get (self, request, unique_id) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        cart = models.Cart.objects.filter(unique_id=unique_id).first()
        if not cart:
            return Response ({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        manager = Manager.objects.filter(cart=cart)
        if not manager.exists():
            return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)
        manager_list = []
        for i in manager:
            history = History.objects.filter(manager=i).first()
            if history:
                date = history.date 
            else:
                date = datetime.datetime.now()
                
            national_code = i.national_code
            name = i.name
            lock = False
            file = None

            
            if history:
                history = serializers.HistorySerializer(history).data
                lock = history['lock']
                file = history['file']
                date = history ['date']

   
            manager_list.append({
                'national_code': national_code,
                'lock': lock,
                'file': file,
                'name': name ,
                'date' : date 
            })

        return Response({'manager': manager_list}, status=status.HTTP_200_OK)




