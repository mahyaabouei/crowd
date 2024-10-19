from django.conf import settings
import requests
from django.core.mail import EmailMessage
import os


class Message():
    def __init__(self,otp,mobile,email):
        self.otp = otp
        self.mobile = mobile
        self.email = email
    def otpSMS(self):
        txt = f'به ایساتیس کراد خوش آمدید \n کد تایید :{self.otp}'
        resp = requests.get(url=f'http://tsms.ir/url/tsmshttp.php?from={settings.SMS_NUMBER}&to={self.mobile}&username={settings.SMS_USERNAME}&password={settings.SMS_PASSWORD}&message={txt}').json()
        print(txt)

    def otpEmail(self):

        print(self.email)


        subject = 'کد تایید ایساتیس کراد'
        message = f'ّکد تایید ورود به ایساتیس کراد شما {self.otp} میباشد'
        recipient_list = [self.email]
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.EMAIL_FROM_ADDRESS,
            to=recipient_list,
            headers={"x-liara-tag": "test-tag"} 
        )
        email.send(fail_silently=False)