from rest_framework.views import APIView
from rest_framework.response import Response
from GuardPyCaptcha.Captch import GuardPyCaptcha
from rest_framework import status 
import requests
from .models import User , Otp , Captcha , Admin , accounts ,addresses ,BlacklistedToken, financialInfo , jobInfo , privatePerson ,tradingCodes , Reagent , legalPersonShareholders , legalPersonStakeholders , LegalPerson
from . import serializers
import datetime
from . import fun
import json
import random
import os
from utils.message import Message
from plan.views import check_legal_person
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit   
from django.utils.decorators import method_decorator
from django.conf import settings


class CaptchaViewset(APIView) :
    """
    This view is used to generate a CAPTCHA code and send it to the user.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get (self,request):
        """
        Generate and send CAPTCHA code.

        This method generates a 4-character numeric CAPTCHA code, stores it in the database, 
        and returns the generated code and CAPTCHA image URL to the user as a response.

        Response:
            captcha: Information about the CAPTCHA, including the encrypted code and image URL.
        
        """
        captcha = GuardPyCaptcha ()
        captcha = captcha.Captcha_generation(num_char=4 , only_num= True)
        Captcha.objects.create(encrypted_response=captcha['encrypted_response'])
        captcha_obj = Captcha.objects.filter(encrypted_response=captcha['encrypted_response'],enabled=True).first()


        return Response ({'captcha' : captcha} , status = status.HTTP_200_OK)


# otp for user
class OtpViewset(APIView) :
    """
    This view is used to verify CAPTCHA and send an OTP code to the user.
    """
    
    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post (self,request) :
        """
        Verify CAPTCHA and send OTP code.

        This method verifies the CAPTCHA, checks if the national code exists in the system, and sends an OTP to the user's mobile.
        
        - If the CAPTCHA is incorrect, an error message is returned.
        - If the CAPTCHA is correct, an OTP code is generated and sent to the user's mobile.
        - If the national code does not exist in the system, an OTP request is sent to an external service.

        Parameters:
            encrypted_response (str): Encrypted CAPTCHA response.
            captcha (str): User-entered CAPTCHA code.
            uniqueIdentifier (str): National ID or unique identifier of the user.

        Responses:
            200: {"message": "OTP has been sent"}
            400: {"message": "Invalid CAPTCHA" / "National ID required" / "Wait 2 minutes to resend OTP"}
        
        """
        encrypted_response = request.data['encrypted_response'].encode()
        captcha_obj = Captcha.objects.filter(encrypted_response=request.data['encrypted_response'],enabled=True).first()
        if not captcha_obj :
            return Response ({'message' : 'کپچا صحیح نیست'} , status=status.HTTP_400_BAD_REQUEST)
        captcha_obj.delete()
        if isinstance(encrypted_response, str):
            encrypted_response = encrypted_response.encode('utf-8')
        captcha = GuardPyCaptcha()

        captcha = captcha.check_response(encrypted_response, request.data['captcha'])
        if not settings.DEBUG : 
            if not captcha :
                return Response ({'message' : 'کد کپچا صحیح نیست'} , status=status.HTTP_400_BAD_REQUEST)
            if request.data['captcha'] == '' :
                return Response ({'message' : 'کد کپچا خالی است'} , status=status.HTTP_400_BAD_REQUEST)

        uniqueIdentifier = request.data['uniqueIdentifier']
        if not uniqueIdentifier :
            return Response ({'message' : 'کد ملی را وارد کنید'} , status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter (uniqueIdentifier = uniqueIdentifier).first()
        
        if user :
            otp = Otp.objects.filter(mobile=user.mobile).first()
            code = random.randint(10000,99999)

            if not otp:
                otp = Otp(mobile=user.mobile, code=code , expire = timezone.now () + timedelta(minutes=2))
            elif otp.expire > timezone.now() :
                return Response({'error': 'برای ارسال کد مجدد 2 دقیقه منتظر بمانید '}, status=status.HTTP_400_BAD_REQUEST)
            elif otp.expire < timezone.now():
                otp.code = code 
                otp.expire = timezone.now () + timedelta(minutes=2)
            otp.save()
            message = Message(code,user.mobile,user.email)
            message.otpSMS()
            # message.otpEmail(code, user.email)
            return Response({'message' : 'کد تایید ارسال شد' },status=status.HTTP_200_OK)
        
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
                return Response ({ 'message' : 'کد تایید ارسال شد'},status=status.HTTP_200_OK)
            return Response ({ 'message' : 'کد تایید ارسال شد'},status=status.HTTP_200_OK)

        return Response ({ 'message' : 'کد تایید ارسال شد'},status=status.HTTP_200_OK)
                

# login or sign up user
class LoginViewset(APIView):
    """
    This view handles the login process, which includes OTP verification and user creation if necessary.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post (self, request) :
        """
        User login process.

        This endpoint verifies the user's OTP and National ID. If valid, it generates a login token. 
        If the user does not exist, it fetches the user details from an external API and creates a new user.
        
        Parameters:
            uniqueIdentifier (str): National ID or unique identifier of the user.
            otp (str): One-Time Password (OTP) sent to the user.
            reference (str, optional): Reference ID for referrals.

        Responses:
            200: {"access": "<JWT token>"}
            400: {"message": "Invalid OTP" / "National ID and OTP are required"}
            429: {"message": "Account locked due to too many attempts"}
        """
        uniqueIdentifier = request.data.get('uniqueIdentifier')
        otp = request.data.get('otp')
        reference = request.data.get('reference')  
        user = None

        if not uniqueIdentifier or not otp:
            return Response({'message': 'کد ملی و کد تأیید الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(uniqueIdentifier=uniqueIdentifier)
            if user.is_locked():
                return Response({'message': 'حساب شما قفل است، لطفاً بعد از مدتی دوباره تلاش کنید.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except  :
            pass
        if user : 
            try:
                mobile = user.mobile
                otp_obj = Otp.objects.filter(mobile=mobile , code = otp ).order_by('-date').first()
                if otp_obj is None:
                    user.attempts += 1  
                    if user.attempts >= 3:
                        user.lock() 
                        return Response({'message': 'تعداد تلاش‌های شما بیش از حد مجاز است. حساب شما برای 5 دقیقه قفل شد.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

                    user.save()  
                    return Response({'message': 'کد تأیید اشتباه است'}, status=status.HTTP_400_BAD_REQUEST)

                if otp_obj.expire and timezone.now() > otp_obj.expire:
                    return Response({'message': 'زمان کد منقضی شده است'}, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                return Response({'message': 'کد تأیید نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)
            user.attempts = 0
            user.save()
            otp_obj.delete()
            token = fun.encryptionUser(user)
            return Response({'access': token}, status=status.HTTP_200_OK)
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
    """
    This view returns the complete profile information for a user, including account details, addresses, 
    personal information, financial information, job information, and  if user is legal person entity legal and stakeholders and shareholders.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get (self,request) :
        """
        Fetches detailed profile information for the authenticated user.

        Returns user's account details, addresses, personal information, financial info, job info,
        and legal person details if applicable.
        """

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
    

#otp for admin
class OtpAdminViewset(APIView) :
    """
    This view is used for generating and sending OTP to admin users after CAPTCHA verification.
    """
    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))

    def post (self,request) :
        """
        Generate and send OTP to admin.

        This endpoint verifies the provided CAPTCHA code, checks the admin's unique identifier, 
        and generates a one-time password (OTP) which is sent to the admin's registered mobile number.

        Parameters:
            encrypted_response (str): Encrypted CAPTCHA response.
            captcha (str): User-entered CAPTCHA code.
            uniqueIdentifier (str): National ID or unique identifier of the admin.

        Responses:
            200: {"message": "OTP has been sent"}
            400: {"message": "Invalid CAPTCHA" / "National ID is required"}
            429: {"error": "Please wait 2 minutes before requesting a new OTP"}
        """
        captcha = GuardPyCaptcha()
        encrypted_response = request.data['encrypted_response']
        captcha_obj = Captcha.objects.filter(encrypted_response=encrypted_response,enabled=True).first()
        if not captcha_obj :
            return Response ({'message' : 'کپچا صحیح نیست'} , status=status.HTTP_400_BAD_REQUEST)
        captcha_obj.delete()
        if isinstance(encrypted_response, str):
            encrypted_response = encrypted_response.encode('utf-8')
        captcha = captcha.check_response(encrypted_response , request.data['captcha'])
        if not settings.DEBUG : 
            if not captcha :
                return Response ({'message' : 'کد کپچا صحیح نیست'} , status=status.HTTP_400_BAD_REQUEST)
            if request.data['captcha'] == '' :
                return Response ({'message' : 'کد کپچا خالی است'} , status=status.HTTP_400_BAD_REQUEST)

        uniqueIdentifier = request.data['uniqueIdentifier']
        if not uniqueIdentifier :
            return Response ({'message' : 'کد ملی را وارد کنید'} , status=status.HTTP_400_BAD_REQUEST)
        admin = Admin.objects.filter(uniqueIdentifier = uniqueIdentifier).first()

        if admin :
            otp = Otp.objects.filter(mobile=admin.mobile).first()
            code = random.randint(10000,99999)

            if not otp:
                otp = Otp(mobile=admin.mobile, code=code , expire = timezone.now () + timedelta(minutes=2))
            elif otp.expire > timezone.now() :
                return Response({'error': 'برای ارسال کد مجدد 2 دقیقه منتظر بمانید '}, status=status.HTTP_400_BAD_REQUEST)
            elif otp.expire < timezone.now():
                otp.code = code 
                otp.expire = timezone.now () + timedelta(minutes=2)
            otp.save()
            message = Message(code,admin.mobile,admin.email)
            message.otpSMS()
        # message.otpEmail(code, admin.email)
            return Response({'message' : 'کد تایید ارسال شد' },status=status.HTTP_200_OK)
    
        return Response({'message' : 'کد تایید ارسال شد' },status=status.HTTP_200_OK)


# login for admin
class LoginAdminViewset(APIView) :
    """
    This view handles admin login using National ID and OTP code.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post (self,request) :
        """
        Authenticate admin login.

        This endpoint verifies the provided National ID and OTP code. If successful, it generates an access token. 
        If the OTP code is incorrect or expired, the admin account will be locked temporarily after multiple failed attempts.

        Parameters:
            uniqueIdentifier (str): National ID or unique identifier of the admin.
            code (str): OTP code sent to the admin.

        Responses:
            200: {"access": "<JWT token>"}
            400: {"message": "Invalid OTP" / "National ID and OTP required"}
            404: {"message": "National ID not found"}
            429: {"message": "Account locked due to too many attempts"}
        
        """
        uniqueIdentifier = request.data.get('uniqueIdentifier')
        code = request.data.get('code')
        if not uniqueIdentifier or not code:
            return Response({'message': 'کد ملی و کد تأیید الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            admin = Admin.objects.get(uniqueIdentifier=uniqueIdentifier)
            if admin.is_locked():
                return Response({'message': 'حساب شما قفل است، لطفاً بعد از مدتی دوباره تلاش کنید.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except admin.DoesNotExist:
            return Response({'message': ' کد ملی  موجود نیست لطفا ثبت نام کنید'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            mobile = admin.mobile
            otp_obj = Otp.objects.filter(mobile=mobile , code = code ).order_by('-date').first()
            if otp_obj is None:
                admin.attempts += 1  
                if admin.attempts >= 3:
                    admin.lock() 
                    return Response({'message': 'تعداد تلاش‌های شما بیش از حد مجاز است. حساب شما برای 5 دقیقه قفل شد.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

                admin.save()  
                return Response({'message': 'کد تأیید اشتباه است'}, status=status.HTTP_400_BAD_REQUEST)

            if otp_obj.expire and timezone.now() > otp_obj.expire:
                return Response({'message': 'زمان کد منقضی شده است'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'message': 'کد تأیید نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)
        admin.attempts = 0
        admin.save()
        otp_obj.delete()
        token = fun.encryptionadmin(admin)
        return Response({'access': token}, status=status.HTTP_200_OK)


# user list for admin
class UserListViewset (APIView) :
    """
    This view returns a list of all users for admin, including detailed information such as addresses, 
    personal info, financial info, job info, and legal entities associated with each user.
    """
    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get (self, request) :
        """
        Retrieves a list of all users for admin with detailed information.

        This endpoint provides a complete list of users for admin, including details such as addresses, 
        personal info, financial info, job info, and legal entities.
        """
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


# user one for admin
class UserOneViewset(APIView) :
    """
    This view returns detailed information for a specific user for admin, including addresses, 
    personal info, financial info, job info, and trading codes.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get (self,request,id) :
        """
        Retrieve detailed information for a specific user by admin.

        This endpoint returns the user’s detailed information, including addresses, personal info, financial info, job info, and trading codes.
        """
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


# otp for update information for admin
class OtpUpdateViewset(APIView) :
    """
    This view allows an admin to send an OTP to a user through the Sejam system.

    Rate limit: Each IP can send up to 5 requests per minute.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post (self,request) :
        """
        Send OTP through Sejam system for a specified user.

        This endpoint sends an OTP to a user through the Sejam system based on the provided National ID.
        """
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
            return Response ({'message' :'ارسال از طریق سجام امکان پذیر نیست '} , status=status.HTTP_400_BAD_REQUEST)
        return Response ({'message' : 'کد تایید از طریق سامانه سجام ارسال شد'},status=status.HTTP_200_OK)
            

# update information for admin
class UpdateInformationViewset(APIView) :
    """
    This view allows an admin to update user information with data received from the Sejam system.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='PATCH', block=True))
    def patch(self, request):
        """
        Update user information based on Sejam data.

        This endpoint allows an admin to update a user's information, including accounts, addresses, and legal entities, with data received from the Sejam system.
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        admin = fun.decryptionadmin(Authorization)
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
    

# add bours code for legal person
class AddBoursCodeUserViewset(APIView):
    """
    This view allows a user to add a Bours (trading) code if they are a legal entity.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post (self, request) :
        """
            Add Bours (trading) code for a legal entity user.

            This endpoint allows a user who is a legal entity to add a Bours code if they are verified as such.
        """
        Authorization = request.headers.get('Authorization')    
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()
        legal = check_legal_person(user.uniqueIdentifier)
        if legal == True :
            bours_code = request.data.get('bours_code')
            if tradingCodes.objects.filter(user=user, code = bours_code).exists():
                return Response({'message': 'Bours code already exists'}, status=status.HTTP_200_OK)
            else:
                trading_code = tradingCodes.objects.create(user=user,code = bours_code)
                serializer = serializers.tradingCodesSerializer(trading_code)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Not a legal person'}, status=status.HTTP_200_OK)
    

# logout for user
class LogoutViewset(APIView):
    """
    This view logs out the user by blacklisting their token.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request):
        """
        Log out the user by blacklisting their token.

        This endpoint logs out the user by adding their token to the blacklist.
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        token = Authorization.split('Bearer ')[1]
        
        black_list = BlacklistedToken.objects.create(token=token)
        print(black_list)
        return Response({'message': 'Successfully logged out'}, status=status.HTTP_201_CREATED)
    





