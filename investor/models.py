from django.db import models
from authentication.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone




def validate_file_size(file):
    max_size = 2024288000
    if file.size > max_size:
        raise ValidationError(f"حجم فایل نباید بیشتر از {max_size / (1024 * 1024)} مگابایت باشد.")

#  کارت درخواست سرمایه پذیر
class Cart (models.Model) :
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length =200)
    Lock_company_name = models.BooleanField(default=False)
    
    activity_industry = models.CharField(max_length =200 , blank = True, null = True) #صنعت فعالیت
    Lock_activity_industry = models.BooleanField(default=False)

    registration_number = models.CharField(max_length = 20 , blank = True, null = True)  #شماره ثبت 
    Lock_registration_number = models.BooleanField(default=False)

    nationalid = models.CharField(max_length = 20 , blank = True, null = True)
    Lock_nationalid = models.BooleanField(default=False)

    registered_capital = models.CharField(max_length = 100,blank = True, null = True ) #سرمایه ثبتی
    Lock_registered_capital = models.BooleanField(default=False)

    personnel = models.IntegerField(blank = True, null = True)
    Lock_personnel = models.BooleanField(default=False)

    OPTION_KIND = [
        ('1', 'سهامی عام'),
        ('2', 'با مسئولیت محدود'),
        ('3', 'تضامنی'),
        ('4', 'مختلط'),
        ('5', 'نسبی'),
        ('6', 'تعاونی'),
        ('7', 'دانش بنیان'),
        ('8', 'سهامی خاص'),
    ]
    company_kind = models.CharField(max_length = 13, choices = OPTION_KIND, blank = True, null = True) #نوع شرکت
    Lock_company_kind = models.BooleanField(default=False)

    amount_of_request = models.CharField(max_length = 150 , blank = True, null = True) #منابع درخواستی
    Lock_amount_of_request = models.BooleanField(default=False)

    code = models.CharField(max_length = 5, blank = True, null = True)
    
    email = models.EmailField(blank = True, null = True)
    Lock_email = models.BooleanField(default=False)
    
    address = models.CharField (max_length=500 , blank = True, null = True)
    Lock_address = models.BooleanField(default=False)

    financial_report_thisyear = models.FileField(upload_to='static/' ,  blank = True, null = True,validators=[validate_file_size])
    Lock_financial_report_thisyear = models.BooleanField(default=False)

    financial_report_lastyear = models.FileField(upload_to='static/' ,  blank = True, null = True,validators=[validate_file_size])
    Lock_financial_report_lastyear = models.BooleanField(default=False)
    financial_report_yearold = models.FileField(upload_to='static/' ,  blank = True, null = True,validators=[validate_file_size])
    Lock_financial_report_yearold = models.BooleanField(default=False)

    audit_report_thisyear = models.FileField(upload_to='static/' ,  blank = True, null = True,validators=[validate_file_size])
    Lock_audit_report_thisyear = models.BooleanField(default=False)

    audit_report_lastyear = models.FileField(upload_to='static/' ,  blank = True, null = True,validators=[validate_file_size])
    Lock_audit_report_lastyear = models.BooleanField(default=False)

    audit_report_yearold = models.FileField(upload_to='static/' ,  blank = True, null = True,validators=[validate_file_size])
    Lock_audit_report_yearold= models.BooleanField(default=False)

    statement_thisyear = models.FileField(upload_to='static/' ,  blank = True, null = True,validators=[validate_file_size])
    Lock_statement_thisyear = models.BooleanField(default=False)

    statement_lastyear = models.FileField(upload_to='static/' ,  blank = True, null = True,validators=[validate_file_size])
    Lock_statement_lastyear = models.BooleanField(default=False)

    statement_yearold = models.FileField(upload_to='static/' ,  blank = True, null = True,validators=[validate_file_size])
    Lock_statement_yearold = models.BooleanField(default=False)

    alignment_6columns_thisyear = models.FileField(upload_to='static/' ,  blank = True, null = True,validators=[validate_file_size])
    Lock_alignment_6columns_thisyear = models.BooleanField(default=False)

    alignment_6columns_lastyear = models.FileField(upload_to='static/' ,  blank = True, null = True,validators=[validate_file_size])
    Lock_alignment_6columns_lastyear = models.BooleanField(default=False)

    alignment_6columns_yearold = models.FileField(upload_to='static/' ,  blank = True, null = True,validators=[validate_file_size])
    Lock_alignment_6columns_yearold = models.BooleanField(default=False)

    creat = models.DateTimeField(default=timezone.now)
    logo = models.FileField(upload_to='static/' ,  blank = True, null = True,validators=[validate_file_size])
    Lock_logo =  models.BooleanField(default=False)

    city = models.CharField(max_length=100 , null=True , blank=True)
    lock_city =  models.BooleanField(default=False)

    postal_code = models.CharField(max_length=15, null=True , blank=True)
    lock_postal_code =  models.BooleanField(default=False)

    newspaper = models.CharField(max_length=20, null=True , blank=True)   #روزنامه رسمی
    Lock_newspaper =  models.BooleanField(default=False)

    date_newspaper = models.DateTimeField(null=True , blank=True)    #تاریخ روزنامه
    Lock_date_newspaper =  models.BooleanField(default=False)

    otc_fee = models.CharField(max_length=150, null=True , blank=True)    #کارمزد فرابورس
    lock_otc_fee = models.BooleanField(default=False)

    publication_fee = models.CharField(max_length=150, null=True , blank=True)    #کارمزد انتشار
    lock_publication_fee = models.BooleanField(default=False)

    dervice_fee = models.CharField(max_length=150, null=True , blank=True)    #کارمزد ارائه خدمات
    lock_dervice_fee = models.BooleanField(default=False)

    design_cost = models.CharField(max_length=150, null=True , blank=True)   #کارمزد طراحی
    lock_v = models.BooleanField(default=False)

    percentage_total_amount = models.CharField(max_length=150, null=True , blank=True) #درصد مبلغ کل تامین مالی
    lock_percentage_total_amount = models.BooleanField(default=False)

    payback_period = models.IntegerField(null=True , blank=True) #دوره بازپرداخت
    lock_payback_period = models.BooleanField(default=False)

    swimming_percentage = models.FloatField(null=True, blank=True) # درصد تامین مالی شناور
    lock_swimming_percentage = models.BooleanField(default=False)

    partnership_interest = models.CharField(max_length=150, null=True , blank=True) # سود مشارکت اسمی
    lock_partnership_interest = models.BooleanField(default=False)

    guarantee = models.CharField(max_length=150, null=True , blank=True) # ضمانت نامه
    lock_guarantee = models.BooleanField(default=False)
    
    amount_of_registered_shares = models.IntegerField( null=True , blank=True) # تعداد سهام ثبتی 
    lock_amount_of_registered_shares = models.BooleanField(default=False) 
    
    exchange_code =  models.CharField(max_length=150, null=True , blank=True) #کد بورسی
    lock_exchange_code = models.BooleanField(default=False) 

    year_of_establishment = models.DateTimeField(null=True, blank=True)
    lock_year_of_establishment = models.BooleanField(default=False) 

    finish_cart =  models.BooleanField(default=False) # اتمام کارت
    
    risk_committee = models.BooleanField(default=False) # کمیته ریسک
    evaluation_committee = models.BooleanField(default=False) #کمیته ارزیابی

    role_141 = models.BooleanField(default=False)  #  ماده 141
    lock_contract = models.BooleanField(default=False) 
    Prohibited = models.BooleanField(default=False)  #  ممنوع العامله
    criminal_record = models.BooleanField(default=False)  #  سابقه ی کیفری
    effective_litigation = models.BooleanField(default=False)  #  دعاوی موثر
    bounced_check = models.BooleanField(default=False)  #  چک برگشتی
    non_current_debt = models.BooleanField(default=False)  #   بدهی غیر جاری
    minimum_deposit_10= models.BooleanField(default=False)  #   واریز حداقل10درصد
    def __str__(self):
        return self.company_name
    

class Message(models.Model):
    cart  = models.ForeignKey(Cart , on_delete=models.CASCADE)
    message = models.CharField(max_length=512 )
    def __str__(self):
        return self.cart.__str__() + self.message
    

class AddInformation (models.Model):
    announcement_of_changes_managers = models.FileField(upload_to='static/' ,  blank = True, null = True) # اگهی اخرین تغیرات مدیران 
    lock_announcement_of_changes_managers = models.BooleanField(default=False)
    
    announcement_of_changes_capital  = models.FileField(upload_to='static/' ,  blank = True, null = True) # اگهی اخرین تغیرات سرمایه ای 
    lock_announcement_of_changes_capital = models.BooleanField(default=False)
    
    bank_account_turnover = models.FileField(upload_to='static/' ,  blank = True, null = True) # گردش حساب بانکی
    lock_bank_account_turnover = models.BooleanField(default=False)
    
    statutes = models.FileField(upload_to='static/' ,  blank = True, null = True) #اساسنامه
    lock_statutes = models.BooleanField(default=False)
    
    assets_and_liabilities = models.FileField(upload_to='static/' ,  blank = True, null = True) #لیست دارایی ها و بدهی ها 
    lock_assets_and_liabilities = models.BooleanField(default=False)
    
    latest_insurance_staf  =models.FileField(upload_to='static/' ,  blank = True, null = True) #اخرین لیست بیمه کارکنان 
    lock_latest_insurance_staf = models.BooleanField(default=False)
    
    claims_status = models.FileField(upload_to='static/' ,  blank = True, null = True) # وضعیت دعاوی
    lock_claims_status = models.BooleanField(default=False)
    
    
    product_catalog = models.FileField(upload_to='static/' ,  blank = True, null = True) # کاتالوگ محصولات
    lock_product_catalog = models.BooleanField(default=False)
    
    licenses = models.FileField(upload_to='static/' ,  blank = True, null = True) # مجوز ها
    lock_licenses = models.BooleanField(default=False)
    
    auditor_representative = models.FileField(upload_to='static/' ,  blank = True, null = True) # معرف حسابرس
    lock_auditor_representative = models.BooleanField(default=False)
    
    announcing_account_number = models.FileField(upload_to='static/' ,  blank = True, null = True) # اعلام شماره حساب
    lock_announcing_account_number = models.BooleanField(default=False)

    cart = models.ForeignKey(Cart, on_delete= models.CASCADE)
    def __str__(self):
        return self.cart.__str__ () 
    



