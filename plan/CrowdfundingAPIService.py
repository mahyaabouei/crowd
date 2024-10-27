import requests
from dataclasses import dataclass
import os
from django.conf import settings
from django.core.files.base import ContentFile
@dataclass
class ProjectFinancingProvider:
    """
    این کلاس برای نگهداری اطلاعات ورودی سرویس "ثبت اطلاعات مشارکت کنندگان در تامین مالی جمعی طرح" طراحی شده است.
    
    فیلدها:
        projectID: شناسه پروژه‌ای که تامین مالی برای آن ثبت می‌شود (رشته).
        nationalID: کد ملی یا شناسه ملی مشارکت کننده (عدد).
        isLegal: نوع مشارکت کننده (شخص حقیقی یا حقوقی) به صورت بولین (True برای شخص حقوقی و False برای شخص حقیقی).
        firstName: نام مشارکت کننده (رشته).
        lastNameOrCompanyName: نام خانوادگی یا نام شرکت مشارکت کننده (رشته).
        providedFinancePrice: مبلغ تامین مالی توسط مشارکت کننده (عدد).
        bourseCode: کد بورسی مشارکت کننده (رشته).
        paymentDate: تاریخ پرداخت به فرمت استاندارد ISO 8601 (رشته).
        shebaBankAccountNumber: شماره حساب شبا متقاضی (رشته).
        mobileNumber: شماره موبایل متقاضی (رشته).
        bankTrackingNumber: کد پیگیری پرداخت از بانک (رشته).
    """
    projectID: str
    nationalID: int
    isLegal: bool
    firstName: str
    lastNameOrCompanyName: str
    providedFinancePrice: int
    bourseCode: str
    paymentDate: str
    shebaBankAccountNumber: str
    mobileNumber: str
    bankTrackingNumber: str

class CrowdfundingAPI:
    """
    این کلاس برای کار با APIهای مختلف سامانه تامین مالی جمعی فرابورس طراحی شده است.
    
    متدها:
        - __init__: سازنده کلاس (بدون نیاز به ورودی) که apiKey را به صورت ثابت تنظیم می‌کند.
        - register_financing: برای ثبت اطلاعات مشارکت کنندگان در تامین مالی یک پروژه.
        - get_company_projects: برای دریافت پروژه‌های تعریف شده توسط یک عامل.
        - get_project_info: برای دریافت اطلاعات یک پروژه.
        - get_project_participation_report: برای دریافت گزارش گواهی مشارکت یک شخص/شرکت در یک پروژه.
    """

    BASE_URL = os.getenv('BASE_URL')
    API_KEY = os.getenv('API_KEY')

    def __init__(self):
        """
        سازنده کلاس (بدون نیاز به ورودی). apiKey به صورت ثابت تنظیم شده است.
        """
        pass

    def register_financing(self, financing_data: ProjectFinancingProvider):
        """
        ثبت اطلاعات مشارکت کنندگان در تامین مالی جمعی طرح.
        
        این متد اطلاعات مالی یک مشارکت کننده را برای یک طرح خاص به سامانه ارسال می‌کند.
        
        پارامترها:
            financing_data: شیءی از کلاس ProjectFinancingProvider که شامل تمامی اطلاعات مورد نیاز برای ثبت تامین مالی است.
            
        خروجی: 
            پاسخ JSON شامل کد پیگیری یا پیام خطا در صورت عدم موفقیت.
        """
        url = f"{self.BASE_URL}/projects/projectfinancingprovider"
        body = {
            "apiKey": self.API_KEY,
            "projectID": financing_data.projectID,
            "NationalID": financing_data.nationalID,
            "IsLegal": financing_data.isLegal,
            "FirstName": financing_data.firstName,
            "LastNameOrCompanyName": financing_data.lastNameOrCompanyName,
            "ProvidedFinancePrice": financing_data.providedFinancePrice,
            "BourseCode": financing_data.bourseCode,
            "PaymentDate": financing_data.paymentDate,
            "ShebaBankAccountNumber": financing_data.shebaBankAccountNumber,
            "MobileNumber": financing_data.mobileNumber,
            "BankTrackingNumber": financing_data.bankTrackingNumber
        }
        response = requests.post(url, json=body)
        return response.json()

    def get_company_projects(self):
        """
        دریافت پروژه‌های تعریف شده توسط یک عامل.
        
        این متد کد پروژه‌های تعریف شده برای یک سکو را برمی‌گرداند.
        
        خروجی:
            یک لیست از شناسه‌های پروژه (Guid) یا پیام خطا در صورت عدم موفقیت.
        """
        url = f"{self.BASE_URL}/projects/GetCompanyProjects"
        body = {
            "apiKey": self.API_KEY
        }
        response = requests.post(url, json=body)
        return response.json()

    def get_project_info(self, project_id: str):
        """
        دریافت اطلاعات یک پروژه.
        
        این متد اطلاعات یک پروژه خاص را برمی‌گرداند.
        
        پارامترها:
            project_id: شناسه پروژه‌ای که اطلاعات آن باید دریافت شود (رشته).
            
        خروجی:
            پاسخ JSON شامل اطلاعات کامل پروژه یا پیام خطا در صورت عدم موفقیت.
        """
        url = f"{self.BASE_URL}/projects/GetProjectInfo"
        body = {
            "apiKey": self.API_KEY, 
            "projectID": project_id
        }
        response = requests.post(url, json=body)
        return response.json()

    def get_project_participation_report(self, project_id: str, national_id: int):
        """
        دریافت گواهی مشارکت در طرح تامین مالی جمعی.
        
        این متد فایل PDF مربوط به گواهی مشارکت یک شخص/شرکت در یک طرح تامین مالی را برمی‌گرداند.
        
        پارامترها:
            project_id: شناسه پروژه (رشته).
            national_id: شناسه ملی / کد ملی مشارکت کننده (عدد).
            
        خروجی:
            پاسخ JSON شامل گواهی مشارکت به صورت PDF یا پیام خطا در صورت عدم موفقیت.
        """
        url = f"{self.BASE_URL}/projects/GetProjectParticipationReport"
        body = {
            "apiKey": self.API_KEY,
            "projectID": project_id,
            "NationalID": national_id
        }
        response = requests.post(url, json=body)
        return response



# مثال استفاده:
# api = CrowdfundingAPI()
# project_data = ProjectFinancingProvider(
#     projectID="3403cbaa-911b-44c3-af6f-de3c97367627",
#     nationalID=1234567890,
#     isLegal=False,
#     firstName="Ali",
#     lastNameOrCompanyName="Seraj",
#     providedFinancePrice=10000,
#     bourseCode="01234SARA",
#     paymentDate="2022-03-06T07:37:15.381Z",
#     shebaBankAccountNumber="IR0696000000010324200001",
#     mobileNumber="09121234567",
#     bankTrackingNumber="3467899953"
# )
# response = api.register_financing(project_data)
# print(response)
