from django.conf import settings
import requests
from django.core.mail import EmailMessage
import os
from email.mime.image import MIMEImage

class UserNotifier:
    def __init__(self, mobile, email):
        self.mobile = '0'+mobile[-10:]
        self.email = email
    


    def send_sms(self, message):
        response = requests.get(
            url=f'http://tsms.ir/url/tsmshttp.php?from={settings.SMS_NUMBER}&to={self.mobile}&username={settings.SMS_USERNAME}&password={settings.SMS_PASSWORD}&message={message}'
        ).json()
        print(self.mobile,'>',message)

    def send_email(self, subject, html_message):
        recipient_list = [self.email]
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.EMAIL_FROM_ADDRESS,
            to=recipient_list
        )
        email.content_subtype = "html"
        
        logo_path = os.path.join(settings.BASE_DIR, "utils/logo.png")
        with open(logo_path, "rb") as f:
            logo = MIMEImage(f.read())
            logo.add_header('Content-ID', '<logo>')
            logo.add_header('Content-Disposition', 'inline', filename="logo.png")
            email.attach(logo)

        email.send()

    def send_otp_sms(self, otp):
        message = f'به ایساتیس کراد خوش آمدید \n کد تایید :{otp}\nisatiscrowd.ir'
        self.send_sms(message)

    def send_otp_email(self, otp):
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
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f0f0f5;
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
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }}
                .logo {{
                    text-align: center;
                    margin-bottom: 25px;
                }}
                .logo img {{
                    max-width: 120px;
                    height: auto;
                }}
                .header {{
                    font-size: 26px;
                    font-weight: bold;
                    color: #2c3e50;
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .content {{
                    font-size: 16px;
                    color: #34495e;
                    line-height: 1.6;
                    margin-bottom: 25px;
                    text-align: center;
                }}
                .code-box {{
                    background-color: #ecf0f1;
                    border: 1px solid #bdc3c7;
                    padding: 15px;
                    font-family: 'Courier New', Courier, monospace;
                    font-size: 20px;
                    color: #e74c3c;
                    overflow-x: auto;
                    word-wrap: break-word;
                    text-align: center;
                    direction: ltr;
                    border-radius: 5px;
                }}
                .footer {{
                    font-size: 12px;
                    color: #95a5a6;
                    text-align: center;
                    margin-top: 30px;
                }}
                a {{
                    color: #3498db;
                    text-decoration: none;
                }}
            </style>
        </head>
        <body>
            <div class="wrapper">
                <div class="container">
                    <!-- Logo Section -->
                    <div class="logo">
                        <img src="cid:logo" />
                    </div>

                    <div class="header">ایساتیس کراد</div>
                    <div class="content">
                        کاربر گرامی, کد تایید برای ورود به حساب کاربری خود را در زیر مشاهده
                        می‌کنید
                    </div>
                    <div class="code-box">{otp}</div>
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
        try :
            self.send_email(subject, html_message)
        except Exception as e :
            pass

    def send_finance_completion_sms(self):
        message = 'طرح تأمین مالی تکمیل شده است. مشارکت شما با موفقیت در فرابورس ثبت شد.'
        self.send_sms(message)

    def send_finance_completion_email(self):
        if not self.email:  # بررسی وجود ایمیل
            print("ایمیل کاربر وجود ندارد. ارسال ایمیل انجام نشد.")
            return  # یا می‌توانید یک پیام خطا به کاربر ارسال کنید

        subject = 'تکمیل طرح تأمین مالی'
        html_message = f'''
        <!DOCTYPE html>
        <html lang="fa">
        <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>تکمیل طرح تأمین مالی</title>
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

                    <div class="header">تکمیل طرح تأمین مالی</div>
                    <div class="content">
                    کاربر گرامی، طرح تأمین مالی تکمیل شده است و مشارکت شما با موفقیت در فرابورس ثبت شد.
                    </div>
                    <div class="footer">
                        از مشارکت شما سپاسگزاریم.
                        <br/>
                        <a href="isatiscrowd.ir">isatiscrowd.ir</a>
                    </div>
                </div>
                </div>
            </body>
            </html>
        '''
        self.send_email(subject, html_message)
  