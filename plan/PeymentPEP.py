import requests
import random
import datetime
from . import models
from persiantools.jdatetime import JalaliDate

class PasargadPaymentGateway:
    def __init__(self):
        """
        سازنده کلاس که اطلاعات پایه شامل آدرس پایه درگاه، نام کاربری و رمز عبور را دریافت می‌کند.
        :param base_url: آدرس پایه API درگاه پرداخت
        :param username: نام کاربری دریافتی از بانک
        :param password: رمز عبور دریافتی از بانک
        """
        self.base_url = 'https://pep.shaparak.ir/dorsa1'
        self.username = 'ERP77049588'
        self.password = '5lVZk9aA!6'
        self.token = None
        self.terminal_number = 77041714
    
    def generator_invoice_number(self):
        date = datetime.datetime.now()
        duplicate_number = False
        while not duplicate_number:
            
            invoice = str(random.randint(100, 999))+str(date.year)+str(date.month)+str(date.day)+str(date.hour)+str(date.minute)+str(random.randint(10,99))
            duplicate_number = models.PaymentGateway.objects.filter(invoice=invoice).count() ==0

        return invoice
    def generator_date(self):
        return str(JalaliDate(datetime.datetime.now())).replace('-', '/')
    def get_token(self):
        """
        دریافت توکن از سرور. توکن برای فراخوانی سایر متدهای API نیاز است.
        :raises: Exception در صورت عدم موفقیت در دریافت توکن
        """
        url = f"{self.base_url}/token/getToken"
        data = {
            "username": self.username,
            "password": self.password
        }
        response = requests.post(url, json=data)
        if response.status_code == 200 and response.json()['resultCode'] == 0:
            self.token = response.json()['token']
        else:
            raise Exception(f"Error getting token: {response.json()}")

    def create_purchase(self,invoice, invoiceDate, amount, callback_url, mobile_number, service_code, payerName,nationalCode, description=""):
        """
        ایجاد تراکنش خرید با اطلاعات مربوط به فاکتور و ارسال درخواست به درگاه.
        
        :param invoice: شماره فاکتور یکتا برای هر تراکنش
        :param amount: مبلغ به ریال
        :param callback_url: آدرس بازگشت کاربر پس از انجام عملیات پرداخت
        :param mobile_number: شماره موبایل پرداخت کننده
        :param service_code: کد سرویس خرید
        :param description: توضیحات مربوط به تراکنش
        :raises: Exception در صورت عدم موفقیت در ایجاد تراکنش خرید
        :returns: آدرس پرداختی تولید شده توسط سرور
        """
        self.get_token()
        if not self.token:
            raise Exception("Token is required. Please call get_token() first.")
        
        url = f"{self.base_url}/api/payment/purchase"
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "invoice": invoice,
            "invoiceDate": invoiceDate,
            "amount": int(amount),
            "callbackApi": callback_url,
            "mobileNumber": mobile_number,
            "serviceCode": service_code,
            "serviceType": "PURCHASE",
            "terminalNumber": self.terminal_number,
            "description": description,
            "payerName":str(payerName),
            "nationalCode":str(nationalCode)
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200 and response.json()['resultCode'] == 0:
            return response.json()['data']
        else:
            raise Exception(f"Error creating purchase: {response.json()}")


    def confirm_transaction(self, invoice, url_id):
        """
        تأیید تراکنش خرید پس از پرداخت کاربر.
        
        :param invoice: شماره فاکتور یکتا که برای ایجاد خرید استفاده شده
        :param url_id: شناسه توکن دریافت شده از وب سرویس پرداخت
        :raises: Exception در صورت عدم موفقیت در تأیید تراکنش
        :returns: اطلاعات تراکنش تأیید شده
        """
        self.get_token()
        if not self.token:
            raise Exception("Token is required. Please call get_token() first.")
        
        url = f"{self.base_url}/api/payment/confirm-transactions"
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "invoice": invoice,
            "urlId": url_id
        }
        response = requests.post(url, json=data, headers=headers)
        print('-'*15)
        print(response.json())
        if response.status_code == 200 and response.json()['resultCode'] == 0:
            return response.json()['data']
        elif response.json()['resultCode'] in [13046]:
            return response.json()
        else:
            raise Exception(f"Error confirming transaction: {response.json()}")

    def verify_transaction(self, invoice, url_id):
        """
        وریفای تراکنش، برای تأییدیه نهایی تراکنش پس از پرداخت.
        
        :param invoice: شماره فاکتور یکتا
        :param url_id: شناسه توکن دریافت شده از وب سرویس پرداخت
        :raises: Exception در صورت عدم موفقیت در وریفای تراکنش
        :returns: وضعیت تراکنش و نتیجه آن
        """
        if not self.token:
            raise Exception("Token is required. Please call get_token() first.")
        
        url = f"{self.base_url}/api/payment/verify-transactions"
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "invoice": invoice,
            "urlId": url_id
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code < 300 or (response.json()['resultCode'] in [0,13046]):
            return response.json()['data']
        else:
            raise Exception(f"Error verifying transaction: {response.json()}")

    def reverse_transaction(self, invoice, url_id):
        """
        برگشت تراکنش، در صورت نیاز به بازگرداندن وجه.
        
        :param invoice: شماره فاکتور یکتا
        :param url_id: شناسه توکن دریافت شده از وب سرویس پرداخت
        :raises: Exception در صورت عدم موفقیت در برگشت تراکنش
        :returns: نتیجه برگشت تراکنش
        """
        if not self.token:
            raise Exception("Token is required. Please call get_token() first.")
        
        url = f"{self.base_url}/api/payment/reverse-transactions"
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "invoice": invoice,
            "urlId": url_id
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200 and response.json()['resultCode'] == 0:
            return response.json()['data']
        else:
            raise Exception(f"Error reversing transaction: {response.json()}")

    def inquiry_transaction(self, invoice):
        """
        استعلام وضعیت تراکنش برای بررسی موفق یا ناموفق بودن آن.
        
        :param invoice: شماره فاکتور یکتا
        :raises: Exception در صورت عدم موفقیت در استعلام وضعیت تراکنش
        :returns: وضعیت فعلی تراکنش
        """
        self.get_token()
        if not self.token:
            raise Exception("Token is required. Please call get_token() first.")
        
        url = f"{self.base_url}/api/payment/payment-inquiry"
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "invoiceId": invoice
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.json().get('data',{'status':response.json().get('resultCode')})
        else:
            raise Exception(f"Error inquiring transaction: {response.json()}")
