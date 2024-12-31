from django.db import models
from authentication.models import User , Admin
from django.utils import timezone
from django.core.exceptions import ValidationError
import magic

def validate_file_type(file):
    valid_mime_types = [
        'image/jpeg', 'image/png', 'application/pdf',
        'application/zip', 'application/x-rar-compressed', 
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document', # docx
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',       # xlsx
        'text/csv', 'application/vnd.ms-excel'                                     # csv, xls
    ]
    
    valid_extensions = ['jpg', 'jpeg', 'png', 'pdf', 'zip', 'rar', 'docx', 'xlsx', 'csv', 'xls']
    
    # بررسی پسوند فایل
    file_extension = file.name.split('.')[-1].lower()
    if file_extension not in valid_extensions:
        raise ValidationError("پسوند فایل پشتیبانی نمی‌شود.")
        
    # بررسی نوع واقعی فایل با استفاده از python-magic
    try:
        mime = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)  # برگرداندن اشاره‌گر فایل به ابتدا
        
        if mime not in valid_mime_types:
            raise ValidationError("نوع فایل پشتیبانی نمی‌شود.")
    except:
        # اگر نتوانستیم نوع فایل را تشخیص دهیم، فقط بر اساس پسوند تصمیم می‌گیریم
        pass



class Plan (models.Model) : 
    trace_code = models.TextField(null=True , blank=True)
    creation_date = models.TextField( null=True , blank=True)
    persian_name =  models.TextField( null=True , blank=True)
    persian_suggested_symbol = models.TextField( null=True , blank=True)
    persoan_approved_symbol = models.TextField( null=True , blank=True)
    english_name = models.TextField( null=True , blank=True)
    english_suggested_symbol = models.TextField( null=True , blank=True)
    english_approved_symbol = models.TextField( null=True , blank=True)
    industry_group_id =  models.BigIntegerField( null=True , blank=True)
    industry_group_description =  models.TextField( null=True , blank=True)
    sub_industry_group_id =  models.TextField( null=True , blank=True)
    sub_industry_group_description =  models.TextField( null=True , blank=True)
    persian_subject =  models.TextField( null=True , blank=True)
    english_subject = models.TextField( null=True , blank=True)
    unit_price = models.BigIntegerField( null=True , blank=True)
    total_units =  models.BigIntegerField( null=True , blank=True)
    company_unit_counts =  models.BigIntegerField( null=True , blank=True)
    total_price =  models.BigIntegerField(null=True, blank=True)
    crowd_funding_type_id  =  models.BigIntegerField( null=True , blank=True)
    crowd_funding_type_description =  models.TextField( null=True , blank=True)
    float_crowd_funding_type_description = models.TextField( null=True , blank=True)
    minimum_required_price =  models.BigIntegerField( null=True, blank=True)
    real_person_minimum_availabe_price =  models.BigIntegerField( null=True, blank=True)
    real_person_maximum_available_price = models.BigIntegerField( null=True, blank=True)
    legal_person_minimum_availabe_price =  models.BigIntegerField( null=True, blank=True)
    legal_person_maximum_availabe_price =  models.BigIntegerField( null=True, blank=True)
    underwriting_duration =   models.BigIntegerField( null=True , blank=True)
    suggested_underwriting_start_date =  models.TextField( null=True , blank=True)
    suggested_underwriting_end_date = models.TextField( null=True , blank=True)
    approved_underwriting_start_date = models.TextField( null=True , blank=True)
    approved_underwriting_end_date = models.TextField( null=True , blank=True)
    project_start_date =   models.TextField( null=True , blank=True)
    project_end_date =  models.TextField( null=True , blank=True)
    settlement_description =  models.TextField( null=True , blank=True)
    project_status_description =  models.TextField( null=True , blank=True)
    project_status_id =   models.BigIntegerField( null=True , blank=True)
    persian_suggested_underwiring_start_date =  models.TextField( null=True , blank=True)
    persian_suggested_underwriting_end_date =  models.TextField( null=True , blank=True)
    persian_approved_underwriting_start_date =  models.TextField( null=True , blank=True)
    persian_approved_underwriting_end_date =  models.TextField( null=True , blank=True)
    persian_project_start_date =  models.TextField( null=True , blank=True)
    persian_project_end_date = models.TextField( null=True , blank=True)
    persian_creation_date =  models.TextField( null=True , blank=True)
    number_of_finance_provider =  models.BigIntegerField( null=True , blank=True)
    sum_of_funding_provided =   models.BigIntegerField( null=True , blank=True)
    def __str__(self) :
        return self.persian_name or "بدون نام"
        
class ProjectOwnerCompan(models.Model):
    plan = models.ForeignKey(Plan , on_delete=models.CASCADE)
    national_id = models.BigIntegerField( null=True, blank=True)
    name = models.TextField( null=True , blank=True)
    compnay_type_id = models.BigIntegerField( null=True , blank=True)
    company_type_description = models.TextField( null=True , blank=True)
    registration_date = models.TextField( null=True , blank=True)
    registration_number = models.TextField( null=True , blank=True)
    economic_id = models.TextField( null=True , blank=True)
    address = models.TextField( null=True , blank=True)
    postal_code = models.TextField( null=True , blank=True)
    phone_number = models.TextField( null=True , blank=True)
    fax_number = models.TextField( null=True , blank=True)
    email_address = models.TextField( null=True , blank=True)

class ListOfProjectBigShareHolders(models.Model):
    plan = models.ForeignKey(Plan , on_delete=models.CASCADE)
    national_id = models.BigIntegerField( null=True, blank=True)
    shareholder_type = models.BigIntegerField( null=True , blank=True)
    first_name =models.TextField( null=True , blank=True)
    last_name = models.TextField( null=True , blank=True)
    share_percent = models.FloatField( null=True , blank=True)


class ListOfProjectBoardMembers(models.Model):
    plan = models.ForeignKey(Plan , on_delete=models.CASCADE)
    national_id = models.BigIntegerField( null=True, blank=True)
    mobile_number = models.TextField( null=True , blank=True)
    email_address = models.TextField( null=True , blank=True)
    organization_post_id = models.BigIntegerField( null=True , blank=True)
    is_agent_from_company = models.BooleanField(null=True , blank=True)
    first_name =models.TextField( null=True , blank=True)
    last_name = models.TextField( null=True , blank=True)
    company_national_id = models.BigIntegerField( null=True, blank=True)
    company_name = models.TextField( null=True , blank=True)
    organization_post_description = models.TextField( null=True , blank=True)


class PicturePlan(models.Model):
    plan = models.ForeignKey(Plan , on_delete=models.CASCADE)
    picture = models.FileField(upload_to='static/' , null=True ,  blank= True ,validators=[validate_file_type])
    def __str__(self) :
        return str(self.plan.persian_name)


class DocumentationFiles(models.Model): #فایل های مستندات
    plan = models.ForeignKey(Plan , on_delete=models.CASCADE)
    title = models.TextField( blank=True , null=True) 
    file = models.FileField(upload_to = 'static/', null=True , blank=True,validators=[validate_file_type])
    def __str__(self) :
        return str (self.title)
    

class Appendices(models.Model): #تضامین 
    plan = models.ForeignKey(Plan , on_delete=models.CASCADE)
    title = models.TextField( blank=True , null=True) 
    file = models.FileField(upload_to = 'static/', null=True , blank=True,validators=[validate_file_type])
    def __str__(self) :
        return str (self.title)
    

class Comment(models.Model):
    comment = models.TextField ( null= True, blank = True) 
    status = models.BooleanField(default=False)
    known =  models.BooleanField(default=False)
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan , on_delete=models.CASCADE)
    answer = models.TextField ( null= True, blank = True) 
    def __str__(self) :
        return str(self.user.uniqueIdentifier) + str(self.comment)
    

class PaymentGateway(models.Model) :
    plan = models.ForeignKey(Plan , on_delete=models.CASCADE)
    user = models.TextField()
    amount = models.BigIntegerField() #تعداد سهم
    value = models.BigIntegerField() #ارزش کل 
    payment_id = models.TextField() #شناسه پرداخت
    description = models.TextField ( null=True, blank=True)
    code = models.TextField ( null=True, blank=True) #کد 
    create_date =  models.DateTimeField(default=timezone.now) # تاریخ ایجاد مشارکت 
    risk_statement = models.BooleanField(default=True) # بیانیه ریسک
    name_status = models.BooleanField (default=False)
    status_option = [
         ('0','0'), #رد شده
         ('1','1'), #در حال بررسی
         ('2','2'), #تایید موقت
         ('3','3'), #تایید نهایی
    ]
    status =  models.CharField (max_length=10 , choices= status_option , default='1' )
    document =  models.BooleanField (default=True)
    picture = models.FileField(null=True, blank = True  , upload_to='static/',validators=[validate_file_type])
    #### Farabourse #####
    send_farabours = models.BooleanField (default=False)
    trace_code_payment_farabourse = models.TextField (null=True, blank=True,default='')
    provided_finance_price_farabourse = models.BigIntegerField (null=True, blank=True,default=0)
    message_farabourse = models.TextField (null=True, blank=True,default='')
    error_no_farabourse = models.BigIntegerField (null=True, blank=True,default=0)
    ######################
    url_id = models.TextField ( null= True , blank=True)
    mobile = models.TextField( null= True , blank=True)
    invoice = models.TextField( null= True , blank=True)
    invoice_date =  models.DateTimeField(null=True, blank=True, default=timezone.now)
    name = models.TextField( null= True , blank=True)
    service_code = models.TextField (max_length = 10 , null= True , blank = True)
    reference_number = models.TextField (null= True , blank = True, default='') #کد ارجاع شاپرک
    track_id = models.TextField (null= True , blank = True, default='') # شماره پیگیری
    code_status_payment = models.TextField (null= True , blank = True, default='') # کد وضعیت پرداخت پاسارگاد
    card_number = models.TextField (null= True , blank = True, default='') # شماره کارت
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self) :
            track_id = 'none' if not self.track_id else str(self.track_id)
            return str(self.user) + ' ' + str(self.plan.persian_name) + ' ' + track_id + ' s['+ str(self.status) + '] F[' + str(self.send_farabours) + '] T[' + str(self.document) + ']'+ ' v[' + str(self.value) + ']'


class Plans (models.Model):
    plan_id = models.TextField()

    def __str__(self) :
         return self.plan_id
    

class InformationPlan (models.Model):
    plan = models.ForeignKey(Plan, on_delete = models.CASCADE)
    rate_of_return = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status_second_option = [
         ('1','1'),
         ('2','2'),
         ('3','3'),
         ('4','4'),
         ('5','5'),
    ]
    status_second = models.CharField (max_length=50 , choices=status_second_option , null=True, blank=True )
    status_show = models.BooleanField (default=False)
    amount_collected_now = models.BigIntegerField (null=True, blank=True)
    payment_date = models.DateTimeField (null=True, blank=True)
    payback_period_option = [
         ('1','1'),
         ('2','2'),
    ]
    payback_period = models.CharField (max_length= 10 , null=True, blank=True , choices=payback_period_option , default='1')
    period_length = models.IntegerField (null=True, blank=True , default=12)
    def __str__(self) :
         return str(self.plan.persian_name)
         

class EndOfFundraising (models.Model) :
    amount_operator = models.BigIntegerField(null=True, blank=True) #مبلغ ادمین
    amount_systemic = models.BigIntegerField(null=True, blank=True) #مبلغ سیستمی
    plan = models.ForeignKey(Plan , on_delete=models.CASCADE)
    type = models.CharField(max_length=100  , null=True, blank=True)
    date_operator = models.DateField(null=True, blank=True) #تاریخ ادمین
    date_systemic = models.DateField(null=True, blank=True) #تاریخ سیستمی
    date_capitalization_operator = models.DateField(null=True, blank=True) #تاریخ ادمین برای سود
    date_capitalization_systemic = models.DateField(null=True, blank=True) #تاریخ سیستمی برای سود
    profit_payment_comment = models.TextField(null=True, blank=True,default='') #توضیحات پرداخت سود
    profit_receipt_comment = models.TextField(null=True, blank=True,default='') #توضیحات دریافت سود
    profit_payment_completed = models.BooleanField(default=False) #تایید پرداخت سود
    profit_receipt_completed = models.BooleanField(default=False) #تایید دریافت سود
    def __str__(self) :
         return self.plan.persian_name + '-' + self.type
       

       
class Warranty (models.Model):
    plan = models.ForeignKey(Plan, on_delete = models.CASCADE)
    kind_of_warranty = models.TextField( blank = True , null = True)
    date = models.DateTimeField (blank = True , null = True)
    exporter = models.TextField ( blank = True , null = True)
    comment = models.TextField ( blank = True , null = True)
    completed = models.BooleanField (default=False)
    def __str__(self):
        return self.plan.persian_name 
    

class Complaint (models.Model):
    plan = models.ForeignKey(Plan, on_delete = models.CASCADE)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    create_at = models.DateTimeField(default=timezone.now)
    title = models.TextField(blank=True, null=True)
    send_farabourse = models.BooleanField(default=False)
    message = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.plan.persian_name 