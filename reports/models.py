from django.db import models
from plan.models import Plan


    
class AuditReport(models.Model): # گزارش حسابرسی
    plan = models.ForeignKey(Plan , on_delete=models.CASCADE)
    title = models.CharField(max_length=150 , blank=True , null=True) 
    file = models.FileField(upload_to = 'static/', null=True , blank=True)
    def __str__(self) :
        return self.title
    

    
class ProgressReport(models.Model): # گزارش پیشرفت 
    plan = models.ForeignKey(Plan , on_delete=models.CASCADE)
    title = models.CharField(max_length=150 , blank=True , null=True) 
    file = models.FileField(upload_to = 'static/', null=True , blank=True)
    def __str__(self) :
        return self.title
    
