from django.conf import settings
import requests
from django.core.mail import EmailMessage
import os
from email.mime.image import MIMEImage


class Message():
    def __init__(self,otp,mobile,email):
        self.otp = otp
        self.mobile = mobile
        self.email = email
    def otpSMS(self):
        txt = f'به ایساتیس کراد خوش آمدید \n کد تایید :{self.otp}\nisatiscrowd.ir'
        resp = requests.get(url=f'http://tsms.ir/url/tsmshttp.php?from={settings.SMS_NUMBER}&to={self.mobile}&username={settings.SMS_USERNAME}&password={settings.SMS_PASSWORD}&message={txt}').json()
    def otpEmail(self):

        subject = 'کد تایید ایساتیس کراد'
        html_message = f'''
    <!DOCTYPE html>
    <html lang="fa">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>کد تایید برای ورود</title>
        <style>
        body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f4f4;
                text-align: center;
            }}
            .wrapper {{
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{
                width: 100%;
                max-width: 600px;
                background-color: #ffffff;
                padding: 20px;
                border: 1px solid #e0e0e0;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            .logo {{
                text-align: center;
                margin-bottom: 20px;
            }}
            .logo img {{
                max-width: 150px;
                height: auto;
            }}
            .header {{
                font-size: 24px;
                font-weight: bold;
                color: #333;
                text-align: center;
                margin-bottom: 20px;
            }}
            .content {{
                font-size: 16px;
                color: #555;
                line-height: 1.5;
                margin-bottom: 20px;
                text-align: center;
            }}
            .code-box {{
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                padding: 15px;
                font-family: monospace;
                font-size: 18px;
                color: #444;
                overflow-x: auto;
                word-wrap: break-word;
                text-align: center;
                direction: ltr;
            }}
            .footer {{
                font-size: 12px;
                color: #777;
                text-align: center;
                margin-top: 20px;
            }}
            </style>
        </head>
        <body>
            <div class="wrapper">
            <div class="container">
                <!-- Logo Section -->
                <div class="logo">
                <img
                    src="cid:logo"  
                />
                </div>

                <div class="header">ایساتیس کراد</div>
                <div class="content">
                کاربر گرامی, کد تایید برای ورود به حساب کاربری خود را در زیر مشاهده
                می‌کنید
                </div>
                <div class="code-box">{self.otp}</div>
                <div class="footer">
                    اگر این درخواست توسط شما صورت نگرفته، لطفاً این ایمیل را نادیده بگیرید.
                    <br/>
                    <a href="isatiscrowd.ir">isatiscrowd.ir</a>
                </div>
            </div>
            </div>
        </body>
        </html>
        '''

        recipient_list = [self.email]
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.EMAIL_FROM_ADDRESS,
            to=recipient_list,
            headers={"x-liara-tag": "test-tag"}
        )
        email.content_subtype = "html" 
        
        logo_path = os.path.join(settings.BASE_DIR, "utils/logo.png") 
        with open(logo_path, "rb") as f:
            logo = MIMEImage(f.read())
            logo.add_header('Content-ID', '<logo>')
            logo.add_header('Content-Disposition', 'inline', filename="logo.png") 
            email.attach(logo)
        try :
            email.send(fail_silently=False)
        except Exception as e :
            pass