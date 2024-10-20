import datetime
from . import serializers
from .models import Cart , Message  , AddInformation 
from rest_framework import status 
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication import fun
from django.http import HttpResponse, HttpResponseNotAllowed
import random
from manager import models


# done
class RequestViewset(APIView):
    def post (self,request):
        Authorization = request.headers.get('Authorization')
        
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)

        user = fun.decryptionUser(Authorization)

        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()

        
        data = request.data.copy()
        if data['date_newspaper'] :

            try:
                timestamp = (int(data['date_newspaper'])/1000)
                data['date_newspaper'] = datetime.datetime.fromtimestamp(timestamp)
            except:
                try:
                    date_str = data['date_newspaper'].rstrip('Z')
                    if '.' in date_str:
                        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
                    else:
                        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
                    data['date_newspaper'] = date_obj
                except ValueError:
                    return Response({'error': 'Invalid timestamp for date_newspaper'}, status=status.HTTP_400_BAD_REQUEST)
        if data['year_of_establishment']  :
            try:
                timestamp = (int(data['year_of_establishment'])/1000)
                data['year_of_establishment'] = datetime.datetime.fromtimestamp(timestamp)
            except:
                try:
                    date_str = data['year_of_establishment'].rstrip('Z')
                    if '.' in date_str:
                        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
                    else:
                        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
                    data['year_of_establishment'] = date_obj
                except ValueError:
                    return Response({'error': 'Invalid timestamp for year_of_establishment'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.CartSerializer(data=data)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            cart = serializer.save(user=user)



            for file_field in ['financial_report_thisyear', 'financial_report_lastyear', 'financial_report_yearold',
                               'audit_report_thisyear', 'audit_report_lastyear', 'audit_report_yearold',
                               'statement_thisyear', 'statement_lastyear', 'statement_yearold',
                               'alignment_6columns_thisyear', 'alignment_6columns_lastyear', 'alignment_6columns_yearold',
                               'announcement_of_changes_managers', 'announcement_of_changes_capital',
                               'bank_account_turnover', 'statutes', 'assets_and_liabilities',
                               'latest_insurance_staf', 'claims_status', 'logo']:

                if request.data.get(file_field) == None:
                    serializer.validated_data[file_field] = request.data.get(file_field)


                if file_field in request.FILES:
                    serializer.validated_data[file_field] = request.FILES[file_field]

            code = random.randint(10000, 99999)
            serializer.code = code
            serializer.save()

            response_data = serializer.data
            response_data['id'] = cart.id
            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get (self,request) :
        Authorization = request.headers.get('Authorization')    
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()   
        cart = Cart.objects.filter(user=user)
        cart  =cart.order_by('-id')
        cart_serializer  =serializers.CartSerializer(cart ,  many = True)
        return Response ({'message' : True ,  'cart': cart_serializer.data} ,  status=status.HTTP_200_OK )
    

# done
class DetailCartViewset(APIView):    
    def get (self,request,id) :
        Authorization = request.headers.get('Authorization')
        
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)

        user = fun.decryptionUser(Authorization)

        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()   
        cart = Cart.objects.filter(id=id).first()
        if not cart:
            return Response({'error': 'cart not found'}, status=status.HTTP_404_NOT_FOUND)
        cart_serializer = serializers.CartSerializer(cart)
        cart_serializer = cart_serializer.data
        cart_serializer['id'] = cart.id

    
        return Response({'message': True, 'cart': cart_serializer}, status=status.HTTP_200_OK)
    

    
    def patch(self,request, id) :
        Authorization = request.headers.get('Authorization')
        
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)

        user = fun.decryptionUser(Authorization)

        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()  
        cart = Cart.objects.filter(id=id).first()
        if not cart:
            return Response({'error': 'cart not found'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data.copy()
        data.pop('code', None)
        if data['date_newspaper'] :

            try:
                timestamp = (int(data['date_newspaper'])/1000)
                data['date_newspaper'] = datetime.datetime.fromtimestamp(timestamp)
            except:
                try:
                    date_str = data['date_newspaper'].rstrip('Z')
                    if '.' in date_str:
                        # اگر رشته شامل میلی‌ثانیه‌ها باشد
                        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
                    else:
                        # اگر رشته شامل میلی‌ثانیه‌ها نباشد
                        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
                    data['date_newspaper'] = date_obj
                except ValueError:
                    return Response({'error': 'Invalid timestamp for date_newspaper'}, status=status.HTTP_400_BAD_REQUEST)
        if data['year_of_establishment'] :
            try:
                timestamp = (int(data['year_of_establishment'])/1000)
                data['year_of_establishment'] = datetime.datetime.fromtimestamp(timestamp)
            except:
                try:
                    date_str = data['year_of_establishment'].rstrip('Z')
                    if '.' in date_str:
                        # اگر رشته شامل میلی‌ثانیه‌ها باشد
                        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
                    else:
                        # اگر رشته شامل میلی‌ثانیه‌ها نباشد
                        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
                    data['year_of_establishment'] = date_obj
                except ValueError:
                    return Response({'error': 'Invalid timestamp for year_of_establishment'}, status=status.HTTP_400_BAD_REQUEST)
        cart_serializer = serializers.CartSerializer(cart, data=data, partial=True)
        if cart_serializer.is_valid():
            cart_serializer.save()
            return Response({'message': 'Cart updated successfully', 'cart': cart_serializer.data}, status=status.HTTP_200_OK)
        return Response(cart_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # def delete(self, request, id):
    #         Authorization = request.headers.get('Authorization')
            
    #         if not Authorization:
    #             return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)

    #         user = fun.decryptionUser(Authorization)

    #         if not user:
    #             return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    #         user = user.first()

    #         cart = Cart.objects.filter(id=id).first()
    #         if not cart:
    #             return Response({'error': 'cart not found'}, status=status.HTTP_404_NOT_FOUND)

    #         cart.delete()
    #         return Response({'message': 'Cart deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    

# done
class CartAdmin(APIView) :
    def get(self , request) :
        Authorization = request.headers.get('Authorization')     

        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        
        admin = admin.first()
        cart = Cart.objects.all().order_by('-id')
        cart_serializer = serializers.CartSerializer(cart , many = True)
        return Response ({'message' : True ,  'cart': cart_serializer.data} ,  status=status.HTTP_200_OK )


    def patch (self , request , id) :
        Authorization = request.headers.get('Authorization')    

        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        
        admin = admin.first()

        cart = Cart.objects.filter(id=id).first()

        if not cart:
            return Response({'error': 'cart not found'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data.copy()
        for file_field in ['financial_report_thisyear', 'financial_report_lastyear', 'financial_report_yearold',
                               'audit_report_thisyear', 'audit_report_lastyear', 'audit_report_yearold',
                               'statement_thisyear', 'statement_lastyear', 'statement_yearold',
                               'alignment_6columns_thisyear', 'alignment_6columns_lastyear', 'alignment_6columns_yearold',
                               'announcement_of_changes_managers', 'announcement_of_changes_capital',
                               'bank_account_turnover', 'statutes', 'assets_and_liabilities',
                               'latest_insurance_staf', 'claims_status', 'logo' ] :
            if file_field in data :
                if 'null' in request.data.get(file_field) or 'undefined' in request.data.get(file_field):
                    setattr(cart, file_field, None)

            if file_field in request.FILES:
                setattr(cart, file_field, request.FILES[file_field])  
        non_file_fields =['city','lock_city', 'company_name', 'Lock_company_name', 'activity_industry',
                            'Lock_activity_industry', 'registration_number', 'Lock_registration_number',
                            'nationalid','Lock_nationalid', 'registered_capital','Lock_registered_capital',
                            'personnel', 'Lock_personnel', 'company_kind', 'amount_of_request', 'code', 
                            'address', 'email', 'postal_code', 'newspaper', 'otc_fee','publication_fee','dervice_fee',
                            'percentage_total_amount','payback_period','swimming_percentage','guarantee',
                            'year_of_establishment','exchange_code','amount_of_registered_shares',
                            'non_current_debt','minimum_deposit_10','bounced_check',
                            'effective_litigation','criminal_record','prohibited','role_141','date_newspaper',
                            'Lock_company_name', 'Lock_activity_industry', 'Lock_registration_number',
                            'Lock_nationalid', 'Lock_registered_capital', 'Lock_personnel','Lock_company_kind',
                            'Lock_amount_of_request',
                            'Lock_email', 'Lock_address', 'Lock_alignment_6columns_yearold', 'Lock_alignment_6columns_lastyear', 'Lock_alignment_6columns_thisyear',
                            'Lock_statement_yearold','Lock_statement_lastyear','Lock_statement_thisyear',
                            'Lock_audit_report_yearold','Lock_audit_report_lastyear','Lock_audit_report_thisyear',
                            'Lock_financial_report_yearold',
                            'Lock_financial_report_lastyear','Lock_financial_report_thisyear','Lock_logo','lock_postal_code','Lock_newspaper','Lock_date_newspaper','lock_otc_fee',
                            'lock_publication_fee','lock_dervice_fee','lock_percentage_total_amount',
                            'lock_payback_period','lock_swimming_percentage','lock_partnership_interest','lock_guarantee',
                            'lock_amount_of_registered_shares',
                            'lock_exchange_code','lock_year_of_establishment','finish_cart','lock_contract',
                            ]
        for field in non_file_fields:
            if field in data:
                value = data.get(field)

                if field in ['personnel', 'payback_period', 'amount_of_registered_shares','swimming_percentage'] and value == '':
                    value = None

                
                if value == 'true':
                    value = True
                elif value == 'false':
                    value = False
                setattr(cart, field, value) 
        
        if 'date_newspaper' in data:
            if data['date_newspaper'] == '' or data['date_newspaper'] is None:
                cart.date_newspaper = None  
            else:
                if isinstance(data['date_newspaper'], str):
                    try:
                        timestamp = int(data['date_newspaper']) / 1000
                        data['date_newspaper'] = datetime.datetime.fromtimestamp(timestamp)
                    except (ValueError, TypeError):
                        try:
                            date_str = data['date_newspaper'].rstrip('Z')   
                            if '.' in date_str:
                                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
                            else:
                                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
                            data['date_newspaper'] = date_obj
                        except ValueError:
                            return Response({'error': 'Invalid timestamp or date format for date_newspaper'}, status=status.HTTP_400_BAD_REQUEST)

                cart.date_newspaper = data['date_newspaper']
        if 'year_of_establishment' in data:
            if data['year_of_establishment'] == '' or data['year_of_establishment'] is None:
                cart.year_of_establishment = None  
            else:
                if isinstance(data['year_of_establishment'], str):
                    try:
                        timestamp = int(data['year_of_establishment']) / 1000
                        data['year_of_establishment'] = datetime.datetime.fromtimestamp(timestamp)
                    except (ValueError, TypeError):
                        try:
                            date_str = data['year_of_establishment'].rstrip('Z') 
                            if '.' in date_str:
                                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
                            else:
                                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
                            data['year_of_establishment'] = date_obj
                        except ValueError:
                            return Response({'error': 'Invalid timestamp or date format for year_of_establishment'}, status=status.HTTP_400_BAD_REQUEST)

                cart.year_of_establishment = data['year_of_establishment']
        cart.save()
        data.pop('code', None)
        if 'status' in data :
            cart.status = data['status']
            
        cart_serializer = serializers.CartSerializer(cart )
    
        return Response(cart_serializer.data, status=status.HTTP_200_OK)


    def delete(self , request , id):
        Authorization = request.headers.get('Authorization')    

        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        
        admin = admin.first()

        cart = Cart.objects.filter(id=id).first()
        if not cart:
            return Response({'error': 'cart not found'}, status=status.HTTP_404_NOT_FOUND)
        cart.delete()
        return Response({'message': 'Cart deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

# done
class DetailCartAdminViewset(APIView):    
    def get (self,request,id) :
        Authorization = request.headers.get('Authorization')
        
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)

        admin = fun.decryptionadmin(Authorization)

        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()   
        cart = Cart.objects.filter(id=id).first()
        if not cart:
            return Response({'error': 'cart not found'}, status=status.HTTP_404_NOT_FOUND)
        cart_serializer = serializers.CartSerializer(cart)
    
        return Response({'message': True, 'cart': cart_serializer.data}, status=status.HTTP_200_OK)
    
# done
class MessageAdminViewSet(APIView):
    def post(self,request,id):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'Admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        cart = Cart.objects.filter(id=id).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = serializers.MessageSerializer(data={**request.data, 'cart': cart.id})
        # اینجا پیامک باید بره
        send_sms = request.query_params.get('send_sms')
        if not serializer.is_valid():
            print(serializer.errors)  
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            message = serializer.save()  
            return Response({'status': True, 'message': serializer.data}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
    

    def get(self , request,id) :
        Authorization = request.headers.get('Authorization')     
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        cart = Cart.objects.filter(id=id).first()
        message = Message.objects.filter(cart=cart).order_by('-id').first()
        message_serializer = serializers.MessageSerializer(message)
        return Response ({'status' : True ,  'message': message_serializer.data} ,  status=status.HTTP_200_OK )


# done
class MessageUserViewSet(APIView):
    def get(self , request,id) :
        Authorization = request.headers.get('Authorization')     
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()
        cart = Cart.objects.filter(id=id).first()
        message = Message.objects.filter(cart=cart).order_by('-id').first()
        if not message: 
            return Response ({'status' : True ,  'message': {"message":"شما هیچ پیامی ندارید"}} ,  status=status.HTTP_200_OK )
        message_serializer = serializers.MessageSerializer(message )
        return Response ({'status' : True ,  'message': message_serializer.data} ,  status=status.HTTP_200_OK )


# done
class AddInformationViewset (APIView) :
    def post (self, request, id) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()
        cart = Cart.objects.filter(id=id).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        addinformation = AddInformation.objects.filter(cart=cart).first()

        if addinformation:

            if request.data.get('announcement_of_changes_managers') == None:
                addinformation.announcement_of_changes_managers = request.data.get('announcement_of_changes_managers')
            if request.data.get('announcement_of_changes_capital') == None:
                addinformation.announcement_of_changes_capital = request.data.get('announcement_of_changes_capital')
            if request.data.get('bank_account_turnover') == None:
                addinformation.bank_account_turnover = request.data.get('bank_account_turnover')
            if request.data.get('statutes') == None:
                addinformation.statutes = request.data.get('statutes')
            if request.data.get('assets_and_liabilities') == None:
                addinformation.assets_and_liabilities = request.data.get('assets_and_liabilities')
            if request.data.get('latest_insurance_staf') == None:
                addinformation.latest_insurance_staf = request.data.get('latest_insurance_staf')
            if request.data.get('claims_status') == None:
                addinformation.claims_status = request.data.get('claims_status')
            if request.data.get('product_catalog') == None:
                addinformation.product_catalog = request.data.get('product_catalog')
            if request.data.get('licenses') == None:
                addinformation.licenses = request.data.get('licenses')
            if request.data.get('auditor_representative') == None:
                addinformation.auditor_representative = request.data.get('auditor_representative')
            if request.data.get('announcing_account_number') == None:
                addinformation.announcing_account_number = request.data.get('announcing_account_number')
                

            # دریافت داده‌های ارسال شده در فایل‌ها (در صورتی که هر کدام ارسال شده باشند)
            if 'announcement_of_changes_managers' in request.FILES:
                addinformation.announcement_of_changes_managers = request.FILES.get('announcement_of_changes_managers')
            if 'announcement_of_changes_capital' in request.FILES:
                addinformation.announcement_of_changes_capital = request.FILES.get('announcement_of_changes_capital')
            if 'bank_account_turnover' in request.FILES:
                addinformation.bank_account_turnover = request.FILES.get('bank_account_turnover')
            if 'statutes' in request.FILES:
                addinformation.statutes = request.FILES.get('statutes')
            if 'assets_and_liabilities' in request.FILES:
                addinformation.assets_and_liabilities = request.FILES.get('assets_and_liabilities')
            if 'latest_insurance_staf' in request.FILES:
                addinformation.latest_insurance_staf = request.FILES.get('latest_insurance_staf')
            if 'claims_status' in request.FILES:
                addinformation.claims_status = request.FILES.get('claims_status')
            if 'product_catalog' in request.FILES:
                addinformation.product_catalog = request.FILES.get('product_catalog')
            if 'licenses' in request.FILES :
                addinformation.licenses = request.FILES.get('licenses')
            if 'auditor_representative' in request.FILES:
                addinformation.auditor_representative = request.FILES.get('auditor_representative')
            if 'announcing_account_number' in request.FILES:
                addinformation.announcing_account_number = request.FILES.get('announcing_account_number')

            # ذخیره تغییرات
            addinformation.save()
            return Response({'message': 'Information updated successfully'}, status=status.HTTP_200_OK)

        data = {
            'announcement_of_changes_managers': request.FILES.get('announcement_of_changes_managers'),
            'announcement_of_changes_capital': request.FILES.get('announcement_of_changes_capital'),
            'bank_account_turnover': request.FILES.get('bank_account_turnover'),
            'statutes': request.FILES.get('statutes'),
            'assets_and_liabilities': request.FILES.get('assets_and_liabilities'),
            'latest_insurance_staf': request.FILES.get('latest_insurance_staf'),
            'claims_status': request.FILES.get('claims_status'),
            'product_catalog': request.FILES.get('product_catalog'),
            'licenses': request.FILES.get('licenses'),
            'auditor_representative': request.FILES.get('auditor_representative'),
            'announcing_account_number': request.FILES.get('announcing_account_number'),
            'cart': cart.id
        }

        serializer = serializers.AddInformationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get (self, request, id) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response ({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response ({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()
        cart = models.Cart.objects.filter(id=id).first()
        if not cart:
            return Response ({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        
        addinformation = AddInformation.objects.filter(cart=cart).first()
        if not addinformation:
            return Response({'error': 'information not found for this cart'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = serializers.AddInformationSerializer(addinformation)
        return Response(serializer.data, status=status.HTTP_200_OK)


# done
class AddInfromationAdminViewset (APIView) :
    def post (self, request, id) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        cart = models.Cart.objects.filter(id=id).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        addinformation = AddInformation.objects.filter(cart=cart).first()
        data = request.data.copy()
        if not addinformation : 
            addinformation = AddInformation(cart=cart)
            addinformation.save()

            
        for file_field in ['announcement_of_changes_managers','announcement_of_changes_capital','bank_account_turnover',
                           'statutes','assets_and_liabilities','latest_insurance_staf','claims_status'
                           ,'product_catalog','licenses','auditor_representative','announcing_account_number']:
            
            if file_field in data:
                field_value = request.data.get(file_field)
                if field_value in ['null', 'undefined', None , '']:
                    setattr(addinformation, file_field, None)

                else:
                    setattr(addinformation, file_field, field_value)

            if file_field in request.FILES:
                setattr(addinformation, file_field, request.FILES.get(file_field))
        non_file_fields =['lock_announcement_of_changes_managers','lock_assets_and_liabilities', 'lock_latest_insurance_staf', 'lock_claims_status', 'lock_product_catalog',
                            'lock_announcement_of_changes_capital', 'lock_licenses',
                            'lock_bank_account_turnover','lock_statutes', 'lock_auditor_representative','Lock_registered_capital',
                             'lock_announcing_account_number', ] 
        for field in non_file_fields:
            if field in data:
                value = data.get(field)
                
                if value == 'true':
                    value = True
                elif value == 'false':
                    value = False
                setattr(addinformation, field, value) 
        
        try:
            addinformation.save()
        except Exception as e:
            return Response({'error': f'Failed to save data: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
        addinformation_serializer = serializers.AddInformationSerializer(addinformation)
        return Response(addinformation_serializer.data, status=status.HTTP_201_CREATED)


    def get (self, request, id) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        cart = models.Cart.objects.filter(id=id).first()
        if not cart:
            return Response ({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        
        addinformation = AddInformation.objects.filter(cart=cart).first()
        if not addinformation:
            return Response({'error': 'information not found for this cart'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = serializers.AddInformationSerializer(addinformation)
        return Response(serializer.data, status=status.HTTP_200_OK)


# done
class FinishCartViewset(APIView):
    def patch (self,request,id) : 
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        cart = models.Cart.objects.filter(id=id).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        finish_cart_value = request.data.get('finish_cart')
        if finish_cart_value is None:
            return Response({'error': 'finish_cart is required'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.CartSerializer(cart, data={'finish_cart': finish_cart_value}, partial=True)
        if serializer.is_valid():
            serializer.save()  
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

# done
# اپدیت کمیته ریسک
class RiskCommitteeViewset(APIView) :
    def post (self, request,id) : 
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        cart = models.Cart.objects.filter(id=id).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        risk_committee = request.data.get('risk_committee')
        if risk_committee is None:
            return Response({'error': 'risk_committee is required'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.CartSerializer(cart, data={'risk_committee': risk_committee}, partial=True)
        if serializer.is_valid():
            serializer.save()  
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response ({'error': 'Cart not found'}, status.HTTP_400_BAD_REQUEST)

    def get (self, request, id) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        cart = models.Cart.objects.filter(id=id).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        risk_committee = cart.risk_committee
        return Response({'risk_committee': risk_committee}, status=status.HTTP_200_OK)
            

# done
# اپدیت کمیته ارزیابی
class EvaluationCommitteeViewset(APIView) :
    def post (self, request,id) : 
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        cart = models.Cart.objects.filter(id=id).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        evaluation_committee = request.data.get('evaluation_committee')
        if evaluation_committee is None:
            return Response({'error': 'evaluation_committee is required'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.CartSerializer(cart, data={'evaluation_committee': evaluation_committee}, partial=True)
        if serializer.is_valid():
            serializer.save()  
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response ({'error': 'Cart not found'}, status.HTTP_400_BAD_REQUEST)
    



    def get (self, request, id) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        cart = models.Cart.objects.filter(id=id).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        evaluation_committee = cart.evaluation_committee
        return Response({'evaluation_committee': evaluation_committee}, status=status.HTTP_200_OK)
            