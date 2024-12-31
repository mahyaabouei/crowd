from django.db import models
from plan.models import Plan
from django.core.exceptions import ValidationError

def validate_file_type(file):
    valid_extensions = ['jpg', 'jpeg', 'png', 'pdf', 'zip', 'rar', 'docx', 'xlsx', 'csv', 'xls']
    
    # بررسی پسوند فایل
    file_extension = file.name.split('.')[-1].lower()
    if file_extension not in valid_extensions:
        raise ValidationError("پسوند فایل پشتیبانی نمی‌شود.")






    
class AuditReport(models.Model): # گزارش حسابرسی
    plan = models.ForeignKey(Plan , on_delete=models.CASCADE)
    title = models.CharField(max_length=150 , blank=True , null=True) 
    file = models.FileField(upload_to = 'static/', null=True , blank=True,validators=[validate_file_type])
    comment = models.TextField(null=True , blank=True, default='')
    completed = models.BooleanField(default=False)
    date = models.DateTimeField(null=True , blank=True)
    period = models.IntegerField(null=True , blank=True)
    def __str__(self) :
        return self.title + ' ' + str(self.date)
    

    
class ProgressReport(models.Model): # گزارش پیشرفت 
    plan = models.ForeignKey(Plan , on_delete=models.CASCADE)
    title = models.CharField(max_length=150 , blank=True , null=True) 
    file = models.FileField(upload_to = 'static/', null=True , blank=True,validators=[validate_file_type])
    comment = models.TextField(null=True , blank=True, default='')
    completed = models.BooleanField(default=False)
    date = models.DateTimeField(null=True , blank=True)
    period = models.IntegerField(null=True , blank=True)
    def __str__(self) :
        return self.title + ' ' + str(self.date)
    

