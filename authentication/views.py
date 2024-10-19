from rest_framework.views import APIView
from rest_framework.response import Response
from GuardPyCaptcha.Captch import GuardPyCaptcha
from rest_framework import status 
import requests
from .models import User , Otp , Admin , accounts ,addresses , financialInfo , jobInfo , privatePerson ,tradingCodes , Reagent , legalPersonShareholders , legalPersonStakeholders , LegalPerson
from . import serializers
import datetime
from . import fun
import json
import random
import os
from utils.message import Message
class CaptchaViewset(APIView) :
    def get (self,request):
        captcha = GuardPyCaptcha ()
        captcha = captcha.Captcha_generation(num_char=4 , only_num= True)
        return Response ({'captcha' : captcha} , status = status.HTTP_200_OK)

# otp for user
class OtpViewset(APIView) :
    def post (self,request) :
        encrypted_response = request.data['encrypted_response'].encode()
        if isinstance(encrypted_response, str):
            encrypted_response = encrypted_response.encode('utf-8')
        captcha = GuardPyCaptcha()
        captcha = captcha.check_response(encrypted_response, request.data['captcha'])
        if not captcha  :
        # if False : 
            return Response ({'message' : 'کد کپچا صحیح نیست'} , status=status.HTTP_400_BAD_REQUEST)
        uniqueIdentifier = request.data['uniqueIdentifier']
        if not uniqueIdentifier :
            return Response ({'message' : 'کد ملی را وارد کنید'} , status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter (uniqueIdentifier = uniqueIdentifier).first()
        if user :
            code = random.randint(10000,99999)
            otp = Otp(mobile=user.mobile , code=code)
            otp.save()
            message = Message(code,user.mobile,user.email)
            message.otpSMS()
            # message.otpEmail(code, user.email)
            return Response({'registered' : True  ,'message' : 'کد تایید ارسال شد' },status=status.HTTP_200_OK)
        
        if not user:
            url = "http://31.40.4.92:8870/otp"
            payload = json.dumps({
            "uniqueIdentifier": uniqueIdentifier
            })
            headers = {
            'X-API-KEY': os.getenv('X-API-KEY'),
            'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code >=300 :
                return Response ({'message' :'شما سجامی نیستید'} , status=status.HTTP_400_BAD_REQUEST)
            return Response ({'registered' :False , 'message' : 'کد تایید از طریق سامانه سجام ارسال شد'},status=status.HTTP_200_OK)

      
        return Response({'registered' : False , 'message' : 'اطلاعات شما یافت نشد'},status=status.HTTP_400_BAD_REQUEST)   
                

        
# sign up for first user sejam
# done
class SignUpViewset(APIView):
    def post (self, request) :
        uniqueIdentifier = request.data.get('uniqueIdentifier')
        otp = request.data.get('otp')
        reference = request.data.get('reference')  

        if not uniqueIdentifier or not otp:
            return Response({'message': 'کد ملی و کد تأیید الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
        
        url = "http://31.40.4.92:8870/information"
        payload = json.dumps({
        "uniqueIdentifier": uniqueIdentifier,
        "otp": otp
        })
        headers = {
        'X-API-KEY': os.getenv('X-API-KEY'),
        'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        response = json.loads(response.content)
        try :
            data = response['data']
        except:
            return Response({'message' :'1دوباره تلاش کن '}, status=status.HTTP_400_BAD_REQUEST)
        if data == None :
            return Response({'message' :'بیشتر تلاش کن '}, status=status.HTTP_400_BAD_REQUEST)
        new_user = User.objects.filter(uniqueIdentifier=uniqueIdentifier).first()
        
        if  not new_user :
            new_user  =User(
                agent = data ['agent'],
                email = data ['email'],
                # legalPerson = data ['legalPerson'],
                # legalPersonShareholders = data ['legalPersonShareholders'],
                # legalPersonStakeholders = data ['legalPersonStakeholders'],
                mobile = data ['mobile'],
                status = data ['status'],
                type = data ['type'],
                uniqueIdentifier = data ['uniqueIdentifier'],
                referal = data ['uniqueIdentifier'],
            )
            new_user.save()
            if reference:
                try :
                   reference_user = User.objects.get(uniqueIdentifier=reference)
                   Reagent.objects.create(reference=reference_user, referrer=new_user)
                except User.DoesNotExist:
                    pass
                
        if len(data['legalPersonStakeholders']) > 0:
                for legalPersonStakeholders_data in data['legalPersonStakeholders'] :
                    new_legalPersonStakeholders = legalPersonStakeholders(
                    user = new_user ,
                    uniqueIdentifier =legalPersonStakeholders_data['uniqueIdentifier'] ,
                    type = legalPersonStakeholders_data['type'],
                    startAt = legalPersonStakeholders_data ['startAt'],
                    positionType = legalPersonStakeholders_data ['positionType'],
                    lastName = legalPersonStakeholders_data ['lastName'],
                    isOwnerSignature = legalPersonStakeholders_data ['isOwnerSignature'],
                    firstName = legalPersonStakeholders_data ['firstName'],
                    endAt = legalPersonStakeholders_data ['endAt'] ,)
                new_legalPersonStakeholders.save()

        if data['legalPerson']:
            new_LegalPerson = LegalPerson(
            user = new_user ,
            citizenshipCountry =data['legalPerson']['citizenshipCountry'] ,
            economicCode = data['legalPerson']['economicCode'],
            evidenceExpirationDate = data['legalPerson'] ['evidenceExpirationDate'],
            evidenceReleaseCompany = data['legalPerson'] ['evidenceReleaseCompany'],
            evidenceReleaseDate = data['legalPerson'] ['evidenceReleaseDate'],
            legalPersonTypeSubCategory = data['legalPerson'] ['legalPersonTypeSubCategory'],
            registerDate = data['legalPerson'] ['registerDate'],
            legalPersonTypeCategory = data['legalPerson'] ['legalPersonTypeCategory'],
            registerPlace = data['legalPerson'] ['registerPlace'] ,
            registerNumber = data['legalPerson'] ['registerNumber'] ,)
            new_LegalPerson.save()

        if len(data['legalPersonShareholders']) > 0:
                for legalPersonShareholders_data in data['legalPersonShareholders'] :
                    new_legalPersonShareholders = legalPersonShareholders(
                    user = new_user ,
                    uniqueIdentifier = legalPersonShareholders_data['uniqueIdentifier'],
                    postalCode = legalPersonShareholders_data ['postalCode'],
                    positionType = legalPersonShareholders_data ['positionType'],
                    percentageVotingRight = legalPersonShareholders_data ['percentageVotingRight'],
                    firstName = legalPersonShareholders_data ['firstName'],
                    lastName = legalPersonShareholders_data ['lastName'],
                    address = legalPersonShareholders_data ['address'] )
                new_legalPersonShareholders.save()
        if len(data['accounts']) > 0:
            for acounts_data in data['accounts'] :
                new_accounts = accounts(
                    user = new_user ,
                    accountNumber = acounts_data['accountNumber'] ,
                    bank = acounts_data ['bank']['name'],
                    branchCity = acounts_data ['branchCity']['name'],
                    branchCode = acounts_data ['branchCode'],
                    branchName = acounts_data ['branchName'],
                    isDefault = acounts_data ['isDefault'],
                    modifiedDate = acounts_data ['modifiedDate'],
                    type = acounts_data ['type'],
                    sheba = acounts_data ['sheba'] ,)
                new_accounts.save()
        if len (data['addresses']) > 0 :
            for addresses_data in data ['addresses']:
                new_addresses = addresses (
                    user = new_user,
                    alley =  addresses_data ['alley'],
                    city =  addresses_data ['city']['name'],
                    cityPrefix =  addresses_data ['cityPrefix'],
                    country = addresses_data ['country']['name'],
                    countryPrefix =  addresses_data ['countryPrefix'],
                    email =  addresses_data ['email'],
                    emergencyTel =  addresses_data ['emergencyTel'],
                    emergencyTelCityPrefix =  addresses_data ['emergencyTelCityPrefix'],
                    emergencyTelCountryPrefix =  addresses_data ['emergencyTelCountryPrefix'],
                    fax =  addresses_data ['fax'],
                    faxPrefix =  addresses_data ['faxPrefix'],
                    mobile =  addresses_data ['mobile'],
                    plaque =  addresses_data ['plaque'],
                    postalCode =  addresses_data ['postalCode'],
                    province =  addresses_data ['province']['name'],
                    remnantAddress =  addresses_data ['remnantAddress'],
                    section =  addresses_data ['section']['name'],
                    tel =  addresses_data ['tel'],
                    website =  addresses_data ['website'],
                )
                new_addresses.save()
            jobInfo_data = data.get('jobInfo')
            if isinstance(jobInfo_data, dict):
                new_jobInfo = jobInfo(
                    user=new_user,
                    companyAddress=jobInfo_data.get('companyAddress', ''),
                    companyCityPrefix=jobInfo_data.get('companyCityPrefix', ''),
                    companyEmail=jobInfo_data.get('companyEmail', ''),
                    companyFax=jobInfo_data.get('companyFax', ''),
                    companyFaxPrefix=jobInfo_data.get('companyFaxPrefix', ''),
                    companyName=jobInfo_data.get('companyName', ''),
                    companyPhone=jobInfo_data.get('companyPhone', ''),
                    companyPostalCode=jobInfo_data.get('companyPostalCode', ''),
                    companyWebSite=jobInfo_data.get('companyWebSite', ''),
                    employmentDate=jobInfo_data.get('employmentDate', ''),
                    job=jobInfo_data.get('job', {}).get('title', ''),
                    jobDescription=jobInfo_data.get('jobDescription', ''),
                    position=jobInfo_data.get('position', ''),
                )

                new_jobInfo.save()


        privatePerson_data = data.get('privatePerson')
        if isinstance(privatePerson_data, dict):
            birthDate = privatePerson_data.get('birthDate', '')
            fatherName = privatePerson_data.get('fatherName', '')
            firstName = privatePerson_data.get('firstName', '')
            gender = privatePerson_data.get('gender', '')
            lastName = privatePerson_data.get('lastName', '')
            placeOfBirth = privatePerson_data.get('placeOfBirth', '')
            placeOfIssue = privatePerson_data.get('placeOfIssue', '')
            seriSh = privatePerson_data.get('seriSh', '')
            serial = privatePerson_data.get('serial', '')
            shNumber = privatePerson_data.get('shNumber', '')
            signatureFile = privatePerson_data.get('signatureFile', None)

            new_privatePerson = privatePerson(
                user=new_user,
                birthDate=birthDate,
                fatherName=fatherName,
                firstName=firstName,
                gender=gender,
                lastName=lastName,
                placeOfBirth=placeOfBirth,
                placeOfIssue=placeOfIssue,
                seriSh=seriSh,
                serial=serial,
                shNumber=shNumber,
                signatureFile=signatureFile
            )
            new_privatePerson.save()

        if len (data['tradingCodes']) > 0 :
            for tradingCodes_data in data ['tradingCodes']:
                new_tradingCodes = tradingCodes (
                    user = new_user,
                    code = tradingCodes_data ['code'],
                    firstPart = tradingCodes_data ['firstPart'],
                    secondPart = tradingCodes_data ['secondPart'],
                    thirdPart = tradingCodes_data ['thirdPart'],
                    type = tradingCodes_data ['type'],
                )
                new_tradingCodes.save()

        financialInfo_data = data.get('financialInfo')

        
        if isinstance(financialInfo_data, dict):
            assetsValue = financialInfo_data.get('assetsValue', '')
            cExchangeTransaction = financialInfo_data.get('cExchangeTransaction', '')
            companyPurpose = financialInfo_data.get('companyPurpose', '')
            financialBrokers = financialInfo_data.get('financialBrokers', '')
            inComingAverage = financialInfo_data.get('inComingAverage', '')
            outExchangeTransaction = financialInfo_data.get('outExchangeTransaction', '')
            rate = financialInfo_data.get('rate', '')
            rateDate = financialInfo_data.get('rateDate', '')
            referenceRateCompany = financialInfo_data.get('referenceRateCompany', '')
            sExchangeTransaction = financialInfo_data.get('sExchangeTransaction', '')
            tradingKnowledgeLevel = financialInfo_data.get('tradingKnowledgeLevel', None)
            transactionLevel = financialInfo_data.get('transactionLevel', None)

            new_financialInfo = financialInfo(
                user=new_user,
                assetsValue=assetsValue,
                cExchangeTransaction=cExchangeTransaction,
                companyPurpose=companyPurpose,
                financialBrokers=financialBrokers,
                inComingAverage=inComingAverage,
                outExchangeTransaction=outExchangeTransaction,
                rate=rate,
                rateDate=rateDate,
                referenceRateCompany=referenceRateCompany,
                sExchangeTransaction=sExchangeTransaction,
                tradingKnowledgeLevel=tradingKnowledgeLevel,
                transactionLevel=transactionLevel,
            )
            new_financialInfo.save()

        token = fun.encryptionUser(new_user)

        return Response({'message': True , 'access' :token} , status=status.HTTP_200_OK)


# done
class InformationViewset (APIView) :
    def get (self,request) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()   
        user = User.objects.filter(id=user.id).first() if user else None
        
        if not user:
            return Response({'error': 'User not found in database'}, status=status.HTTP_404_NOT_FOUND)
        serializer_user = serializers.UserSerializer(user).data
        user_accounts = accounts.objects.filter(user=user)
        serializer_accounts = serializers.accountsSerializer(user_accounts , many = True).data
        user_addresses = addresses.objects.filter(user=user)
        serializer_addresses = serializers.addressesSerializer(user_addresses , many = True).data
        user_privatePerson = privatePerson.objects.filter(user=user)
        serializer_privatePerson = serializers.privatePersonSerializer(user_privatePerson , many = True).data
        user_financialInfo = financialInfo.objects.filter(user=user)
        serializer_financialInfo = serializers.financialInfoSerializer(user_financialInfo , many = True).data
        user_jobInfo = jobInfo.objects.filter(user=user)
        serializer_jobInfo = serializers.jobInfoSerializer(user_jobInfo , many = True).data
        user_tradingCodes = tradingCodes.objects.filter(user=user)
        serializer_tradingCodes = serializers.tradingCodesSerializer(user_tradingCodes , many = True).data
        user_legalPersonStakeholders = legalPersonStakeholders.objects.filter(user=user)
        serializer_legalPersonStakeholders = serializers.legalPersonStakeholdersSerializer(user_legalPersonStakeholders , many = True).data
        user_LegalPerson = LegalPerson.objects.filter(user=user)
        serializer_LegalPerson = serializers.legalPersonStakeholdersSerializer(user_LegalPerson , many = True).data
        user_legalPersonShareholders = legalPersonShareholders.objects.filter(user=user)
        serializer_legalPersonShareholders = serializers.legalPersonStakeholdersSerializer(user_legalPersonShareholders , many = True).data
        combined_data = {
            **serializer_user,  
            'accounts': serializer_accounts,   
            'addresses': serializer_addresses,  
            'private_person': serializer_privatePerson,  
            'financial_info': serializer_financialInfo,  
            'job_info': serializer_jobInfo,    
            'trading_codes': serializer_tradingCodes,     
            'legalPersonStakeholders': serializer_legalPersonStakeholders,     
            'LegalPerson': serializer_LegalPerson,     
            'legalPersonShareholders': serializer_legalPersonShareholders,     
        }
        return Response({'received_data': True ,  'acc' : combined_data})
    
    def patch (self , request) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()
        user = User.objects.filter(id=user.id).first() if user else None
        if not user:
            return Response({'error': 'User not found in database'}, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data
        if not data:
            return Response({'error': 'No data provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        acc_data = data.get('acc')
        if not acc_data:
            return Response({'error': 'No acc data provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        user_serializer = serializers.UserSerializer(user, data=acc_data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        related_models = {
            'accounts': (accounts, serializers.accountsSerializer),
            'addresses': (addresses, serializers.addressesSerializer),
            'private_person': (privatePerson, serializers.privatePersonSerializer),
            'financial_info': (financialInfo, serializers.financialInfoSerializer),
            'job_info': (jobInfo, serializers.jobInfoSerializer),
            'trading_codes': (tradingCodes, serializers.tradingCodesSerializer),
        }

        for key, (model, serializer_class) in related_models.items():
            if key in acc_data:
                instances_data = acc_data[key]
                for instance_data in instances_data:
                    instance = model.objects.filter(user=user, id=instance_data.get('id')).first()
                    if instance:
                        serializer = serializer_class(instance, data=instance_data, partial=True)
                        if serializer.is_valid():
                            serializer.save()
                        else:
                            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Data updated successfully'})



# login for user
# done
class LoginViewset(APIView) :
    def post (self,request) :
        uniqueIdentifier = request.data.get('uniqueIdentifier')
        otp = request.data.get('otp')
        if not uniqueIdentifier or not otp:
            return Response({'message': 'کد ملی و کد تأیید الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(uniqueIdentifier=uniqueIdentifier)
        except:
            result = {'message': ' کد ملی  موجود نیست لطفا ثبت نام کنید'}
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        
        try:
            mobile = user.mobile
            otp_obj = Otp.objects.filter(mobile=mobile , code = otp ).order_by('-date').first()
            if otp_obj is None : 
                return Response({'message' : 'otp ذخیره نمیشود'},status=status.HTTP_404_NOT_FOUND)
        except :
            return Response({'message': 'کد تأیید نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)
        
        otp = serializers.OtpSerializer(otp_obj).data
        if otp['code']== None :
            result = {'message': 'کد تأیید نامعتبر است'}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
        otp = serializers.OtpSerializer(otp_obj).data
        if 'date' in otp:
            dt = datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.fromisoformat(otp['date'].replace("Z", "+00:00"))
        else  :
            return Response({"error": "Date field is missing in OTP data."}, status=400)
        
        dt = datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(otp['date'].replace("Z", "+00:00"))
        dt = dt.total_seconds()

        if dt >120 :
            result = {'message': 'زمان کد منقضی شده است'}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    
        otp_obj.delete()
        token = fun.encryptionUser(user)
        return Response({'access': token} , status=status.HTTP_200_OK)


#otp for admin
# done
class OtpAdminViewset(APIView) :
    def post (self,request) :
        captcha = GuardPyCaptcha()
        encrypted_response = request.data['encrypted_response']
        if isinstance(encrypted_response, str):
            encrypted_response = encrypted_response.encode('utf-8')
        captcha = captcha.check_response(encrypted_response , request.data['captcha'])
        if not captcha  :
        # # if False : 
            return Response ({'message' : 'کد کپچا صحیح نیست'} , status=status.HTTP_400_BAD_REQUEST)
        uniqueIdentifier = request.data['uniqueIdentifier']
        if not uniqueIdentifier :
            return Response ({'message' : 'کد ملی را وارد کنید'} , status=status.HTTP_400_BAD_REQUEST)
        try :
            admin = Admin.objects.get(uniqueIdentifier = uniqueIdentifier)
        except Admin.DoesNotExist:
            return Response({'error': 'Admin not found'}, status=404)

        admin.save()
        mobile = admin.mobile
        email= admin.email
        code = random.randint(10000,99999)
        otp = Otp( mobile=mobile, code=code)
        otp.save()
        message = Message(code,mobile,email)
        message.otpSMS()
        return Response({'registered' : True , 'message' : 'کد تایید ارسال شد'}  ,status=status.HTTP_200_OK)
    


# login for admin
# done
class LoginAdminViewset(APIView) :
    def post (self,request) :
        uniqueIdentifier = request.data.get('uniqueIdentifier')
        code = request.data.get('code')
        if not uniqueIdentifier or not code:
            return Response({'message': 'کد ملی و کد تأیید الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            admin = Admin.objects.get(uniqueIdentifier=uniqueIdentifier)
        except:
            result = {'message': ' کد ملی  موجود نیست لطفا ثبت نام کنید'}
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        
        try:
            mobile = admin.mobile
            otp_obj = Otp.objects.filter(mobile=mobile , code = code ).order_by('-date').first()
        except :
            return Response({'message': 'کد تأیید نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)
        
        otp = serializers.OtpSerializer(otp_obj).data
        if otp['code']== None :
            result = {'message': 'کد تأیید نامعتبر است'}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
        otp = serializers.OtpSerializer(otp_obj).data
        dt = datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(otp['date'].replace("Z", "+00:00"))
     

        
        dt = dt.total_seconds()

        if dt >120 :
            result = {'message': 'زمان کد منقضی شده است'}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
        otp_obj.delete()
        token = fun.encryptionadmin(admin)
        return Response({'access': token} , status=status.HTTP_200_OK)


# done
class UserListViewset (APIView) :
    def get (self, request) :
        Authorization = request.headers.get('Authorization')    
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        user = User.objects.all()
        user_serializer = serializers.UserSerializer(user,many=True).data
        user_list = []

        for i, user_data in enumerate(user_serializer):
            i_user = user[i]  
            privateperson = privatePerson.objects.filter(user=i_user)
            privateperson_serializer = serializers.privatePersonSerializer(privateperson, many=True).data
            
            user_addresses = addresses.objects.filter(user=i_user)
            serializer_addresses = serializers.addressesSerializer(user_addresses , many=True).data
            
            user_financialInfo = financialInfo.objects.filter(user=i_user)
            serializer_financialInfo = serializers.financialInfoSerializer(user_financialInfo , many=True).data
            
            user_jobInfo = jobInfo.objects.filter(user=i_user)
            serializer_jobInfo = serializers.jobInfoSerializer(user_jobInfo , many=True).data
            
            user_tradingCodes = tradingCodes.objects.filter(user=i_user)
            serializer_tradingCodes = serializers.tradingCodesSerializer(user_tradingCodes , many=True).data
            
            legal_person_shareholder = legalPersonShareholders.objects.filter(user=i_user)
            serializer_legal_person_shareholder = serializers.legalPersonShareholdersSerializer(legal_person_shareholder , many=True).data

            legal_person = LegalPerson.objects.filter(user=i_user)
            serializer_legal_person = serializers.LegalPersonSerializer(legal_person , many=True).data

            legal_person_stakeholders = legalPersonStakeholders.objects.filter(user=i_user)
            serializer_legal_person_stakeholders = serializers.legalPersonStakeholdersSerializer(legal_person_stakeholders , many=True).data

            combined_data = {
                **user_data,  
                'addresses': serializer_addresses,
                'private_person': privateperson_serializer,
                'financial_info': serializer_financialInfo,
                'job_info': serializer_jobInfo,
                'trading_codes': serializer_tradingCodes,
                'legal_person_shareholder': serializer_legal_person_shareholder,
                'legal_person': serializer_legal_person,
                'legal_person_stakeholders': serializer_legal_person_stakeholders,
            }
            
            user_list.append(combined_data)

        return Response(user_list, status=status.HTTP_200_OK)


# done
class UserOneViewset(APIView) :
    def get (self,request,id) :
        Authorization = request.headers.get('Authorization')    
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        user = User.objects.filter(id=id).first()
        user_serializer = serializers.UserSerializer(user).data
        privateperson = privatePerson.objects.filter(user=user)
        privateperson_serializer = serializers.privatePersonSerializer(privateperson, many=True).data

        user_addresses = addresses.objects.filter(user=user)
        serializer_addresses = serializers.addressesSerializer(user_addresses, many=True).data

        user_financialInfo = financialInfo.objects.filter(user=user)
        serializer_financialInfo = serializers.financialInfoSerializer(user_financialInfo, many=True).data

        user_jobInfo = jobInfo.objects.filter(user=user)
        serializer_jobInfo = serializers.jobInfoSerializer(user_jobInfo, many=True).data

        user_tradingCodes = tradingCodes.objects.filter(user=user)
        serializer_tradingCodes = serializers.tradingCodesSerializer(user_tradingCodes, many=True).data

        combined_data = {
            **user_serializer, 
            'addresses': serializer_addresses,
            'private_person': privateperson_serializer,
            'financial_info': serializer_financialInfo,
            'job_info': serializer_jobInfo,
            'trading_codes': serializer_tradingCodes,
        }

        return Response({'success': combined_data}, status=status.HTTP_200_OK)

# done
class OtpUpdateViewset(APIView) :
    def post (self,request) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        uniqueIdentifier = request.data.get("uniqueIdentifier")
        if not uniqueIdentifier :
            return Response ({'errot' : 'uniqueIdentifier not found '} ,  status=status.HTTP_400_BAD_REQUEST) 
        user = User.objects.filter(uniqueIdentifier=uniqueIdentifier).first()
        if user:
            url = "http://31.40.4.92:8870/otp"
            payload = json.dumps({
            "uniqueIdentifier": uniqueIdentifier
            })
            headers = {
            'X-API-KEY': os.getenv('X-API-KEY'),
            'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code >=300 :
                return Response ({'message' :'سجام هم گردنت نمیگیره '} , status=status.HTTP_400_BAD_REQUEST)
            return Response ({'registered' :False , 'message' : 'کد تایید از طریق سامانه سجام ارسال شد'},status=status.HTTP_200_OK)

        return Response({'registered' : False , 'message' : 'سیستم قطع است خداحافظ'},status=status.HTTP_400_BAD_REQUEST)   
                


# done
class UpdateInformationViewset(APIView) :
    def patch(self, request):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        admin = fun.decryptionUser(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        
        admin = admin.first()
        
        otp = request.data.get('otp')
        uniqueIdentifier = request.data.get('uniqueIdentifier')
        if not otp:
            return Response({'error': 'otp not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        url = "http://31.40.4.92:8870/information"
        payload = json.dumps({
            "uniqueIdentifier": uniqueIdentifier,
            "otp": otp
        })
        headers = {
            'X-API-KEY': os.getenv('X-API-KEY'),
            'Content-Type': 'application/json'
        }
        
        response = requests.request("POST", url, headers=headers, data=payload)
        response = json.loads(response.content)
        try:
            data = response['data']
        except:
            return Response({'message': 'دوباره تلاش کن'}, status=status.HTTP_400_BAD_REQUEST)
        
        if data is None:
            return Response({'message': 'بیشتر تلاش کن'}, status=status.HTTP_400_BAD_REQUEST)
        
        new_user = User.objects.filter(uniqueIdentifier=uniqueIdentifier).first()
        
        if new_user:
            new_user.agent = data.get('agent', new_user.agent)
            new_user.email = data.get('email', new_user.email)
            # new_user.legalPerson = data.get('legalPerson', new_user.legalPerson)
            # new_user.legalPersonShareholders = data.get('legalPersonShareholders', new_user.legalPersonShareholders)
            # new_user.legalPersonStakeholders = data.get('legalPersonStakeholders', new_user.legalPersonStakeholders)
            new_user.mobile = data.get('mobile', new_user.mobile)
            new_user.status = data.get('status', new_user.status)
            new_user.type = data.get('type', new_user.type)
            new_user.referal = data.get('uniqueIdentifier', new_user.referal)
            new_user.save()

            if len(data['accounts']) > 0:
                for account_data in data['accounts']:
                    account_obj, created = accounts.objects.update_or_create(
                        user=new_user,
                        accountNumber=account_data['accountNumber'],
                        defaults={
                            'bank': account_data['bank']['name'],
                            'branchCity': account_data['branchCity']['name'],
                            'branchCode': account_data['branchCode'],
                            'branchName': account_data['branchName'],
                            'isDefault': account_data['isDefault'],
                            'modifiedDate': account_data['modifiedDate'],
                            'type': account_data['type'],
                            'sheba': account_data['sheba']
                        }
                    )
            if len(data['legalPersonStakeholders']) > 0:
                for legalPersonStakeholders_data in data['legalPersonStakeholders'] :
                    new_legalPersonStakeholders = legalPersonStakeholders(
                    user = new_user ,
                    uniqueIdentifier =legalPersonStakeholders_data['uniqueIdentifier'] ,
                    type = legalPersonStakeholders_data['type'],
                    startAt = legalPersonStakeholders_data ['startAt'],
                    positionType = legalPersonStakeholders_data ['positionType'],
                    lastName = legalPersonStakeholders_data ['lastName'],
                    isOwnerSignature = legalPersonStakeholders_data ['isOwnerSignature'],
                    firstName = legalPersonStakeholders_data ['firstName'],
                    endAt = legalPersonStakeholders_data ['endAt'] ,)
                new_legalPersonStakeholders.save()

            if data['legalPerson']:
                new_LegalPerson = LegalPerson(
                user = new_user ,
                citizenshipCountry =data['legalPerson']['citizenshipCountry'] ,
                economicCode = data['legalPerson']['economicCode'],
                evidenceExpirationDate = data['legalPerson'] ['evidenceExpirationDate'],
                evidenceReleaseCompany = data['legalPerson'] ['evidenceReleaseCompany'],
                evidenceReleaseDate = data['legalPerson'] ['evidenceReleaseDate'],
                legalPersonTypeSubCategory = data['legalPerson'] ['legalPersonTypeSubCategory'],
                registerDate = data['legalPerson'] ['registerDate'],
                legalPersonTypeCategory = data['legalPerson'] ['legalPersonTypeCategory'],
                registerPlace = data['legalPerson'] ['registerPlace'] ,
                registerNumber = data['legalPerson'] ['registerNumber'] ,)
                new_LegalPerson.save()

            if len(data['legalPersonShareholders']) > 0:
                for legalPersonShareholders_data in data['legalPersonShareholders'] :
                    new_legalPersonShareholders = legalPersonShareholders(
                    user = new_user ,
                    uniqueIdentifier = legalPersonShareholders_data['uniqueIdentifier'],
                    postalCode = legalPersonShareholders_data ['postalCode'],
                    positionType = legalPersonShareholders_data ['positionType'],
                    percentageVotingRight = legalPersonShareholders_data ['percentageVotingRight'],
                    firstName = legalPersonShareholders_data ['firstName'],
                    lastName = legalPersonShareholders_data ['lastName'],
                    address = legalPersonShareholders_data ['address'] )
                new_legalPersonShareholders.save()
            if len(data['addresses']) > 0:
                for address_data in data['addresses']:
                    address_obj, created = addresses.objects.update_or_create(
                        user=new_user,
                        postalCode=address_data['postalCode'],
                        defaults={
                            'alley': address_data.get('alley', ''),
                            'city': address_data['city']['name'],
                            'cityPrefix': address_data.get('cityPrefix', ''),
                            'country': address_data['country']['name'],
                            'countryPrefix': address_data.get('countryPrefix', ''),
                            'email': address_data.get('email', ''),
                            'emergencyTel': address_data.get('emergencyTel', ''),
                            'emergencyTelCityPrefix': address_data.get('emergencyTelCityPrefix', ''),
                            'emergencyTelCountryPrefix': address_data.get('emergencyTelCountryPrefix', ''),
                            'fax': address_data.get('fax', ''),
                            'faxPrefix': address_data.get('faxPrefix', ''),
                            'mobile': address_data.get('mobile', ''),
                            'plaque': address_data.get('plaque', ''),
                            'province': address_data['province']['name'],
                            'remnantAddress': address_data.get('remnantAddress', ''),
                            'section': address_data['section']['name'],
                            'tel': address_data.get('tel', ''),
                            'website': address_data.get('website', '')
                        }
                    )

            jobInfo_data = data.get('jobInfo')
            if isinstance(jobInfo_data, dict):
                jobInfo_obj, created = jobInfo.objects.update_or_create(
                    user=new_user,
                    defaults={
                        'companyAddress': jobInfo_data.get('companyAddress', ''),
                        'companyCityPrefix': jobInfo_data.get('companyCityPrefix', ''),
                        'companyEmail': jobInfo_data.get('companyEmail', ''),
                        'companyFax': jobInfo_data.get('companyFax', ''),
                        'companyFaxPrefix': jobInfo_data.get('companyFaxPrefix', ''),
                        'companyName': jobInfo_data.get('companyName', ''),
                        'companyPhone': jobInfo_data.get('companyPhone', ''),
                        'companyPostalCode': jobInfo_data.get('companyPostalCode', ''),
                        'companyWebSite': jobInfo_data.get('companyWebSite', ''),
                        'employmentDate': jobInfo_data.get('employmentDate', ''),
                        'job': jobInfo_data.get('job', {}).get('title', ''),
                        'jobDescription': jobInfo_data.get('jobDescription', ''),
                        'position': jobInfo_data.get('position', '')
                    }
                )
            
            privatePerson_data = data.get('privatePerson')
            if isinstance(privatePerson_data, dict):
                privatePerson_obj, created = privatePerson.objects.update_or_create(
                    user=new_user,
                    defaults={
                        'birthDate': privatePerson_data.get('birthDate', ''),
                        'fatherName': privatePerson_data.get('fatherName', ''),
                        'firstName': privatePerson_data.get('firstName', ''),
                        'gender': privatePerson_data.get('gender', ''),
                        'lastName': privatePerson_data.get('lastName', ''),
                        'placeOfBirth': privatePerson_data.get('placeOfBirth', ''),
                        'placeOfIssue': privatePerson_data.get('placeOfIssue', ''),
                        'seriSh': privatePerson_data.get('seriSh', ''),
                        'serial': privatePerson_data.get('serial', ''),
                        'shNumber': privatePerson_data.get('shNumber', ''),
                        'signatureFile': privatePerson_data.get('signatureFile', None)
                    }
                )

            financialInfo_data = data.get('financialInfo')
            if isinstance(financialInfo_data, dict):
                financialInfo_obj, created = financialInfo.objects.update_or_create(
                    user=new_user,
                    defaults={
                        'assetsValue': financialInfo_data.get('assetsValue', ''),
                        'cExchangeTransaction': financialInfo_data.get('cExchangeTransaction', ''),
                        'companyPurpose': financialInfo_data.get('companyPurpose', ''),
                        'financialBrokers': financialInfo_data.get('financialBrokers', ''),
                        'inComingAverage': financialInfo_data.get('inComingAverage', ''),
                        'outExchangeTransaction': financialInfo_data.get('outExchangeTransaction', ''),
                        'rate': financialInfo_data.get('rate', ''),
                        'rateDate': financialInfo_data.get('rateDate', ''),
                        'referenceRateCompany': financialInfo_data.get('referenceRateCompany', ''),
                        'sExchangeTransaction': financialInfo_data.get('sExchangeTransaction', ''),
                        'tradingKnowledgeLevel': financialInfo_data.get('tradingKnowledgeLevel', None),
                        'transactionLevel': financialInfo_data.get('transactionLevel', None)
                    }
                )


        return Response({'success': True}, status=status.HTTP_200_OK)