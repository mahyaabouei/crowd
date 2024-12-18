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



class ManagerViewset(APIView):
    """
    This view allows users to manage and retrieve managers associated with a specific cart, identified by its unique ID.
    """
    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request, unique_id):
        """
        Add or update managers for a specific cart.

        This method authenticates the user using the Authorization header and associates a list of managers 
        with a specific cart identified by its unique ID. If managers already exist for the cart, they are removed 
        before adding the new list.

        - If the Authorization header is missing, an error is returned.
        - If the user's authorization token is invalid or the user is not found, an error is returned.
        - If the cart with the specified unique ID does not exist, an error is returned.
        - If manager data is invalid, an error is returned.

        Parameters:
            - Authorization (str, header): User's authorization token.
            - unique_id (str, path): Unique identifier for the cart.
            - managers (list, body): List of manager data to be associated with the cart.

        Responses:
            200: {
                "message": True,
                "data": {
                    "id": <cart_id>,
                    "unique_id": <unique_id>,
                    "managers": [
                        {
                            "name": <manager_name>,
                            "position": <manager_position>,
                            ...
                        },
                        ...
                    ]
                }
            }
            400: {"error": "Authorization header is missing" / "Invalid data"}
            404: {"error": "User not found" / "Cart not found"}
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
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
    
    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get (self,request , unique_id):
        """
        Retrieve managers for a specific cart by unique ID.

        This method authenticates the user using the Authorization header and retrieves all managers associated
        with a cart identified by its unique ID.

        - If the Authorization header is missing, an error is returned.
        - If the user's authorization token is invalid or the user is not found, an error is returned.
        - If the cart with the specified unique ID does not exist, an error is returned.

        Parameters:
            - Authorization (str, header): User's authorization token.
            - unique_id (str, path): Unique identifier for the cart.

        Responses:
            200: {
                "message": True,
                "data": [
                    {
                        "name": <manager_name>,
                        "position": <manager_position>,
                        ...
                    },
                    ...
                ]
            }
            400: {"error": "Authorization header is missing"}
            404: {"error": "User not found" / "Cart not found"}
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()
        cart = models.Cart.objects.filter(unique_id=unique_id).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        
        managers = Manager.objects.filter(cart=cart)
        serializer = serializers.ManagerSerializer(managers, many=True)
        return Response({'message': True, 'data': serializer.data}, status=status.HTTP_200_OK)
    

class ManagerAdminViewset(APIView):
    """
    This view allows admins to retrieve and manage (add/update) managers associated with a specific cart, identified by its unique ID.
    """
    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get(self, request, unique_id):
        """
        Retrieve managers for a specific cart by unique ID.

        This method authenticates the admin using the Authorization header and retrieves all managers associated
        with a cart identified by its unique ID.

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - If the cart with the specified unique ID does not exist, an error is returned.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - unique_id (str, path): Unique identifier for the cart.

        Responses:
            200: {
                "message": True,
                "data": [
                    {
                        "name": <manager_name>,
                        "position": <manager_position>,
                        "national_code": <national_code>,
                        ...
                    },
                    ...
                ]
            }
            400: {"error": "Authorization header is missing"}
            404: {"error": "admin not found" / "Cart not found"}
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        cart = models.Cart.objects.filter(unique_id=unique_id).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        
        managers = Manager.objects.filter(cart=cart)
        serializer = serializers.ManagerSerializer(managers, many=True)
        return Response({'message': True ,  'data': serializer.data }, status=status.HTTP_200_OK)
    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request, unique_id):
        """
        Add or update managers for a specific cart.

        This method authenticates the admin using the Authorization header and associates or updates a list of managers 
        with a specific cart identified by its unique ID. Existing managers with matching national codes will be updated.

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - If the cart with the specified unique ID does not exist, an error is returned.
        - If manager data is invalid or missing required fields, an error is returned.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - unique_id (str, path): Unique identifier for the cart.
            - managers (list, body): List of manager data to be associated with or updated in the cart.

        Responses:
            200: {
                "message": True,
                "data": [
                    {
                        "name": <manager_name>,
                        "position": <manager_position>,
                        "national_code": <national_code>,
                        ...
                    },
                    ...
                ]
            }
            400: {"error": "Authorization header is missing" / "Manager national_code is missing" / "Invalid data"}
            404: {"error": "admin not found" / "Cart not found"}
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)

        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
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


class ResumeViewset(APIView):
    """
    This view allows users to upload and retrieve resumes associated with managers of a specific cart, identified by the cart's unique ID.
    """
    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request, unique_id):
        """
        Upload resumes for managers of a specific cart.

        This method authenticates the user using the Authorization header and allows them to upload resumes 
        associated with managers in a cart identified by its unique ID. If a resume already exists for a 
        manager, it is replaced with the new upload.

        - If the Authorization header is missing, an error is returned.
        - If the user's authorization token is invalid or the user is not found, an error is returned.
        - If the cart with the specified unique ID or any specified manager does not exist, an error is returned.

        Parameters:
            - Authorization (str, header): User's authorization token.
            - unique_id (str, path): Unique identifier for the cart.
            - files (dict, form-data): Each file should be named with the national code of the manager to associate it.

        Responses:
            200: {"success": True}
            400: {"error": "Authorization header is missing" / "Invalid data"}
            404: {"error": "User not found" / "Cart not found" / "Management not found"}
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
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

    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get (self,request,unique_id) :
        """
        Retrieve resumes for managers associated with a specific cart.

        This method authenticates the user using the Authorization header and retrieves all resumes associated 
        with managers in a cart identified by its unique ID, including details such as the manager's national code,
        name, file URL, and lock status.

        - If the Authorization header is missing, an error is returned.
        - If the user's authorization token is invalid or the user is not found, an error is returned.
        - If the cart or associated managers do not exist, an error is returned.

        Parameters:
            - Authorization (str, header): User's authorization token.
            - unique_id (str, path): Unique identifier for the cart.

        Responses:
            200: {
                "manager": [
                    {
                        "national_code": <manager_national_code>,
                        "name": <manager_name>,
                        "lock": <lock_status>,
                        "file": <file_url>,
                    },
                    ...
                ]
            }
            400: {"error": "Authorization header is missing"}
            404: {"error": "User not found" / "Cart not found" / "Manager not found"}
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
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


class ResumeAdminViewset(APIView):
    """
    This view allows admins to retrieve and manage (add/update) resumes associated with managers for a specific cart, identified by its unique ID.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get(self, request, unique_id):
        """
        Retrieve resumes for managers associated with a specific cart by unique ID.

        This method authenticates the admin using the Authorization header and retrieves all resumes associated
        with managers in a cart identified by its unique ID. It includes details such as the manager's national code,
        name, file URL, and lock status.

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - If the cart or associated managers do not exist, an error is returned.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - unique_id (str, path): Unique identifier for the cart.

        Responses:
            200: {
                "manager": [
                    {
                        "national_code": <manager_national_code>,
                        "name": <manager_name>,
                        "lock": <lock_status>,
                        "file": <file_url>,
                    },
                    ...
                ]
            }
            400: {"error": "Authorization header is missing"}
            404: {"error": "admin not found" / "Cart not found" / "Manager not found"}
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
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
    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request, unique_id):
        """
        Add or update resumes for managers of a specific cart.

        This method authenticates the admin using the Authorization header and associates or updates resumes
        for managers in a cart identified by its unique ID. Existing resumes are replaced by new uploads where provided,
        and lock status can be updated as specified.

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - If the cart or manager specified does not exist, an error is returned.
        - If required data or files are missing, an error is returned.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - unique_id (str, path): Unique identifier for the cart.
            - files (dict, form-data): Each file should be named with the national code of the manager.
            - lock statuses (dict, body): Lock statuses, formatted as "<national_code>_lock": true/false.

        Responses:
            201: {
                "managers": [
                    {
                        "national_code": <manager_national_code>,
                        "file": <file_url>,
                        "lock": <lock_status>
                    },
                    ...
                ]
            }
            400: {"error": "Authorization header is missing" / "Not found management for national_code <code>"}
            404: {"error": "admin not found" / "Cart not found"}
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'Admin not found'}, status=status.HTTP_404_NOT_FOUND)
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


class ShareholderViewset(APIView):
    """
    This view allows users to manage (add/update) and retrieve shareholders associated with a specific cart, identified by its unique ID.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request, unique_id):
        """
        Add or update shareholders for a specific cart.

        This method authenticates the user using the Authorization header and allows them to associate a list 
        of shareholders with a specific cart identified by its unique ID. Existing shareholders are removed 
        before adding the new list.

        - If the Authorization header is missing, an error is returned.
        - If the user's authorization token is invalid or the user is not found, an error is returned.
        - If the cart with the specified unique ID does not exist, an error is returned.
        - If shareholder data is invalid, an error is returned.

        Parameters:
            - Authorization (str, header): User's authorization token.
            - unique_id (str, path): Unique identifier for the cart.
            - shareholder (list, body): List of shareholder data to be associated with the cart.

        Responses:
            200: {
                "message": True,
                "data": [
                    {
                        "name": <shareholder_name>,
                        "national_id": <shareholder_national_id>,
                        "percentage": <ownership_percentage>,
                        ...
                    },
                    ...
                ]
            }
            400: {"error": "Authorization header is missing" / "Invalid data"}
            404: {"error": "User not found" / "Cart not found"}
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
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



    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get (self, request , unique_id) :
        """
        Retrieve shareholders for a specific cart by unique ID.

        This method authenticates the user using the Authorization header and retrieves all shareholders associated
        with a cart identified by its unique ID.

        - If the Authorization header is missing, an error is returned.
        - If the user's authorization token is invalid or the user is not found, an error is returned.
        - If the cart with the specified unique ID does not exist, an error is returned.

        Parameters:
            - Authorization (str, header): User's authorization token.
            - unique_id (str, path): Unique identifier for the cart.

        Responses:
            200: {
                "message": True,
                "data": [
                    {
                        "name": <shareholder_name>,
                        "national_id": <shareholder_national_id>,
                        "percentage": <ownership_percentage>,
                        ...
                    },
                    ...
                ]
            }
            400: {"error": "Authorization header is missing"}
            404: {"error": "User not found" / "Cart not found"}
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()
        cart = models.Cart.objects.filter(unique_id=unique_id).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        
        shareholder = Shareholder.objects.filter(cart=cart)
        serializer = serializers.ShareholderSerializer(shareholder, many=True)
        return Response({'message': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class ShareholderAdminViewset(APIView):
    """
    This view allows admins to manage (add/update) and retrieve shareholders associated with a specific cart, identified by its unique ID.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get(self, request, unique_id):
        """
        Retrieve shareholders for a specific cart by unique ID.

        This method authenticates the admin using the Authorization header and retrieves all shareholders associated
        with a cart identified by its unique ID.

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - If the cart with the specified unique ID does not exist, an error is returned.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - unique_id (str, path): Unique identifier for the cart.

        Responses:
            200: {
                "message": True,
                "data": [
                    {
                        "name": <shareholder_name>,
                        "national_id": <shareholder_national_id>,
                        "percentage": <ownership_percentage>,
                        ...
                    },
                    ...
                ]
            }
            400: {"error": "Authorization header is missing"}
            404: {"error": "admin not found" / "Cart not found"}
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        cart = models.Cart.objects.filter(unique_id=unique_id).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        
        shareholder = Shareholder.objects.filter(cart=cart)
        serializer = serializers.ShareholderSerializer(shareholder, many=True)
        return Response({'message': True ,  'data': serializer.data }, status=status.HTTP_200_OK)

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self,request,unique_id) :
        """
        Add or update shareholders for a specific cart.

        This method authenticates the admin using the Authorization header and allows them to associate a list 
        of shareholders with a specific cart identified by its unique ID. Existing shareholders are removed 
        before adding the new list.

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - If the cart with the specified unique ID does not exist, an error is returned.
        - If shareholder data is invalid, an error is returned.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - unique_id (str, path): Unique identifier for the cart.
            - shareholder (list, body): List of shareholder data to be associated with the cart.

        Responses:
            200: {
                "message": True,
                "data": [
                    {
                        "name": <shareholder_name>,
                        "national_id": <shareholder_national_id>,
                        "percentage": <ownership_percentage>,
                        ...
                    },
                    ...
                ]
            }
            400: {"error": "Authorization header is missing" / "Invalid data"}
            404: {"error": "admin not found" / "Cart not found"}
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
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


class ValidationViewset(APIView):
    """
    This view allows users to upload and retrieve validation files associated with managers for a specific cart, identified by the cart's unique ID.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request, unique_id):
        """
        Upload validation files for managers of a specific cart.

        This method authenticates the user using the Authorization header and allows them to upload validation files 
        associated with managers in a cart identified by its unique ID. Existing validation files are replaced.

        - If the Authorization header is missing, an error is returned.
        - If the user's authorization token is invalid or the user is not found, an error is returned.
        - If the cart or any specified manager does not exist, an error is returned.

        Parameters:
            - Authorization (str, header): User's authorization token.
            - unique_id (str, path): Unique identifier for the cart.
            - files (dict, form-data): Each file should be named with the national code of the manager or "1" for the company.
            - dates (dict, body): Dates in milliseconds associated with each file, formatted as "<national_code>_date".

        Responses:
            200: {
                "data": {
                    "managers": [
                        {
                            "national_code": <manager_national_code>,
                            "name": <manager_name>,
                            "file_manager": <file_url>,
                            "date": <validation_date>
                        },
                        ...
                    ]
                }
            }
            400: {"error": "Authorization header is missing" / "Invalid data"}
            404: {"error": "User not found" / "Cart not found" / "Manager with national code <code> not found for this cart"}
            500: {"error": "<Exception message>"}
        """
        try:
            Authorization = request.headers.get('Authorization')
            if not Authorization:
                return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = fun.decryptionUser(Authorization)
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
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


    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get(self, request, unique_id):
        """
        Retrieve validation files for managers associated with a specific cart.

        This method authenticates the user using the Authorization header and retrieves all validation files 
        associated with managers in a cart identified by its unique ID, including file URLs and validation dates.

        - If the Authorization header is missing, an error is returned.
        - If the user's authorization token is invalid or the user is not found, an error is returned.
        - If the cart or associated managers do not exist, an error is returned.

        Parameters:
            - Authorization (str, header): User's authorization token.
            - unique_id (str, path): Unique identifier for the cart.

        Responses:
            200: {
                "data": {
                    "managers": [
                        {
                            "national_code": <manager_national_code>,
                            "name": <manager_name>,
                            "file_manager": <file_url>,
                            "date": <validation_date>
                        },
                        ...
                    ]
                }
            }
            400: {"error": "Authorization header is missing"}
            404: {"error": "User not found" / "Cart not found" / "No managers found for this cart"}
            500: {"error": "<Exception message>"}
        """
        try:
            Authorization = request.headers.get('Authorization')
            if not Authorization:
                return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = fun.decryptionUser(Authorization)
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
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
                
                print(validation)

                if validation:
                    date = validation.date
                else:
                    date = datetime.datetime.now()

                print(date)
                

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
            print(f"An error occurred: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ValidationAdminViewset(APIView):
    """
    This view allows admins to upload and retrieve validation files with lock status for managers and the company associated with a specific cart, identified by the cart's unique ID.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request, unique_id):
        """
        Upload or update validation files for managers of a specific cart, with lock status.

        This method authenticates the admin using the Authorization header and allows them to upload validation files 
        associated with managers and the company in a cart identified by its unique ID. Existing validation files are replaced.
        Lock statuses can also be set for each manager.

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - If the cart or any specified manager does not exist, an error is returned.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - unique_id (str, path): Unique identifier for the cart.
            - files (dict, form-data): Each file should be named with the national code of the manager or "1" for the company.
            - dates (dict, body): Dates in milliseconds associated with each file, formatted as "<national_code>_date".
            - lock statuses (dict, body): Lock statuses, formatted as "lock_<national_code>": true/false.

        Responses:
            200: {
                "data": {
                    "managers": [
                        {
                            "national_code": <manager_national_code>,
                            "name": <manager_name>,
                            "file_manager": <file_url>,
                            "date": <validation_date>,
                            "lock": <lock_status>
                        },
                        ...
                    ]
                }
            }
            400: {"error": "Authorization header is missing" / "File validation is missing"}
            404: {"error": "admin not found" / "Cart not found" / "Manager with national code <code> not found for this cart"}
            500: {"error": "<Exception message>"}
        """
        try :
            Authorization = request.headers.get('Authorization')
            if not Authorization:
                return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
            admin = fun.decryptionadmin(Authorization)
            if not admin:
                return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
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
            print(f"An error occurred: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get (self, request, unique_id) :
        """
        Retrieve validation files for managers associated with a specific cart, including lock status.

        This method authenticates the admin using the Authorization header and retrieves all validation files 
        associated with managers in a cart identified by its unique ID, including file URLs, validation dates, 
        and lock statuses.

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - If the cart or associated managers do not exist, an error is returned.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - unique_id (str, path): Unique identifier for the cart.

        Responses:
            200: {
                "data": {
                    "managers": [
                        {
                            "national_code": <manager_national_code>,
                            "name": <manager_name>,
                            "file_manager": <file_url>,
                            "date": <validation_date>,
                            "lock": <lock_status>
                        },
                        ...
                    ]
                }
            }
            400: {"error": "Authorization header is missing"}
            404: {"error": "admin not found" / "Cart not found" / "No managers found for this cart"}
            500: {"error": "<Exception message>"}
        """
        try :
            Authorization = request.headers.get('Authorization')
            if not Authorization:
                return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
            admin = fun.decryptionadmin(Authorization)
            if not admin:
                return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
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
            print(f"An error occurred: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HistoryViewset(APIView):
    """
    This view allows users to upload and retrieve historical records (files and dates) associated with managers for a specific cart, identified by the cart's unique ID.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request, unique_id):

        """
        Retrieve historical records for managers associated with a specific cart.

        This method authenticates the user using the Authorization header and retrieves all historical records 
        associated with managers in a cart identified by its unique ID, including file URLs, dates, and lock status.

        - If the Authorization header is missing, an error is returned.
        - If the user's authorization token is invalid or the user is not found, an error is returned.
        - If the cart or associated managers do not exist, an error is returned.

        Parameters:
            - Authorization (str, header): User's authorization token.
            - unique_id (str, path): Unique identifier for the cart.

        Responses:
            200: {
                "manager": [
                    {
                        "national_code": <manager_national_code>,
                        "name": <manager_name>,
                        "file": <file_url>,
                        "date": <history_date>,
                        "lock": <lock_status>
                    },
                    ...
                ]
            }
            400: {"error": "Authorization header is missing"}
            404: {"error": "User not found" / "Cart not found" / "Manager not found"}
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
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

                print(f"Date for manager {manager.national_code}: {date}")  
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



    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get (self, request, unique_id) :
        """
        Retrieve historical records for managers associated with a specific cart.

        This method authenticates the user using the Authorization header and retrieves all historical records 
        associated with managers in a cart identified by its unique ID, including file URLs, dates, and lock status.

        - If the Authorization header is missing, an error is returned.
        - If the user's authorization token is invalid or the user is not found, an error is returned.
        - If the cart or associated managers do not exist, an error is returned.

        Parameters:
            - Authorization (str, header): User's authorization token.
            - unique_id (str, path): Unique identifier for the cart.

        Responses:
            200: {
                "manager": [
                    {
                        "national_code": <manager_national_code>,
                        "name": <manager_name>,
                        "file": <file_url>,
                        "date": <history_date>,
                        "lock": <lock_status>
                    },
                    ...
                ]
            }
            400: {"error": "Authorization header is missing"}
            404: {"error": "User not found" / "Cart not found" / "Manager not found"}
        """
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


class HistoryAdminViewset(APIView):
    """
    This view allows admins to upload and retrieve historical records (files and dates) with lock status associated with managers for a specific cart, identified by the cart's unique ID.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request, unique_id):
        """
        Upload or update historical records for managers of a specific cart, with lock status.

        This method authenticates the admin using the Authorization header and allows them to upload historical files 
        associated with managers in a cart identified by its unique ID. Existing historical records are replaced with the new uploads.
        Lock statuses and dates can also be set for each manager.

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - If the cart or any specified manager does not exist, an error is returned.
        - If date data for any manager is missing or in an invalid format, an error is returned.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - unique_id (str, path): Unique identifier for the cart.
            - files (dict, form-data): Each file should be named with the national code of the manager.
            - dates (dict, body): Dates in milliseconds associated with each file, formatted as "<national_code>_date".
            - lock statuses (dict, body): Lock statuses, formatted as "lock_<national_code>": true/false.

        Responses:
            200: {
                "managers": [
                    {
                        "national_code": <manager_national_code>,
                        "name": <manager_name>,
                        "file": <file_url>,
                        "date": <history_date>,
                        "lock": <lock_status>
                    },
                    ...
                ]
            }
            400: {"error": "Authorization header is missing" / "Date for manager with national code <code> is missing" / "Invalid date format for manager <code>" / "Lock status for manager <code> is missing"}
            404: {"error": "admin not found" / "Cart not found" / "Not found management for national_code <code>"}
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
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
                print(history)
                

                

        
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
      

    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get (self, request, unique_id) :
        """
        Retrieve historical records for managers associated with a specific cart, including lock status.

        This method authenticates the admin using the Authorization header and retrieves all historical records 
        associated with managers in a cart identified by its unique ID, including file URLs, dates, and lock statuses.

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - If the cart or associated managers do not exist, an error is returned.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - unique_id (str, path): Unique identifier for the cart.

        Responses:
            200: {
                "manager": [
                    {
                        "national_code": <manager_national_code>,
                        "name": <manager_name>,
                        "file": <file_url>,
                        "date": <history_date>,
                        "lock": <lock_status>
                    },
                    ...
                ]
            }
            400: {"error": "Authorization header is missing"}
            404: {"error": "admin not found" / "Cart not found" / "Manager not found"}
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
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




