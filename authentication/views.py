from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from GuardPyCaptcha.Captch import GuardPyCaptcha
from rest_framework import status 
import requests
from . import models
from . import serializers
import datetime
from . import fun


class CaptchaViewset(APIView) :
    def get (self,request):
        captcha = GuardPyCaptcha ()
        captcha = captcha.Captcha_generation(num_char=4 , only_num= True)
        return Response ({'captcha' : captcha} , status = status.HTTP_200_OK)
    

class OtpViewset(APIView) :
    def post (self,request) :
        captcha = GuardPyCaptcha()
        captcha = captcha.check_response(request.data['encrypted_response'] , request.data['captcha'])
        if False : 
            return Response ({'message' : 'کد کپچا صحیح نیست'} , status=status.HTTP_400_BAD_REQUEST)
        national_code = request.data['national_code']
        if not national_code :
            return Response ({'message' : 'کد ملی را وارد کنید'} , status=status.HTTP_400_BAD_REQUEST)
        user = models.User.objects.get(national_code = national_code)
        if not user :
            return Response ({'message' : 'ورود با سجام'})
        user.save()
        mobile = user.mobile
        result = {'registered' : True , 'message' : 'کد تایید ارسال شد'}    
        code = 11111 #random.randint(10000,99999)
        otp = models.Otp(user=user, mobile=mobile, code=code)
        otp.save()
        # SendSms(mobile ,code)
        return Response(result,status=status.HTTP_200_OK)

class LoginViewset(APIView) :
    def post (self,request) :
        national_code = request.data.get('national_code')
        code = request.data.get('code')
        if not national_code or not code:
            return Response({'message': 'کد ملی و کد تأیید الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = models.User.objects.get(national_code=national_code)
        except:
            result = {'message': ' کد ملی  موجود نیست لطفا ثبت نام کنید'}
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        
        try:
            mobile = user.mobile
            otp_obj = models.Otp.objects.filter(mobile=mobile , code = code ).order_by('-date').first()
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
        token = fun.encryptionUser(user)
        return Response({'access': token} , status=status.HTTP_200_OK)
    