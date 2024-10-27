from django.db import models
from plan.models import Plan
from django.core.exceptions import ValidationError

def validate_file_type(file):
    valid_mime_types = [
        'image/jpeg', 'image/png', 'application/pdf',
        'application/zip', 'application/x-rar-compressed', 
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document', # docx
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',       # xlsx
        'text/csv', 'application/vnd.ms-excel'                                     # csv, xls
    ]
    
    valid_extensions = ['jpg', 'jpeg', 'png', 'pdf', 'zip', 'rar', 'docx', 'xlsx', 'csv', 'xls']
    
    file_mime_type = file.content_type
    file_extension = file.name.split('.')[-1].lower()

    if file_mime_type not in valid_mime_types or file_extension not in valid_extensions:
        raise ValidationError("Unsupported file type.")






    
class AuditReport(models.Model): # گزارش حسابرسی
    plan = models.ForeignKey(Plan , on_delete=models.CASCADE)
    title = models.CharField(max_length=150 , blank=True , null=True) 
    file = models.FileField(upload_to = 'static/', null=True , blank=True,validators=[validate_file_type])
    def __str__(self) :
        return self.title
    

    
class ProgressReport(models.Model): # گزارش پیشرفت 
    plan = models.ForeignKey(Plan , on_delete=models.CASCADE)
    title = models.CharField(max_length=150 , blank=True , null=True) 
    file = models.FileField(upload_to = 'static/', null=True , blank=True,validators=[validate_file_type])
    def __str__(self) :
        return self.title
    
