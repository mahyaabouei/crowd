from django.contrib import admin
from . import models
from openpyxl import Workbook
from django.http import HttpResponse
from django.utils import timezone

def remove_timezone(dt):
    if dt and dt.tzinfo:
        return dt.replace(tzinfo=None)
    return dt

admin.site.register(models.Plan)
admin.site.register(models.Plans)
admin.site.register(models.ProjectOwnerCompan)
admin.site.register(models.ListOfProjectBoardMembers)
admin.site.register(models.ListOfProjectBigShareHolders)
admin.site.register(models.DocumentationFiles)
admin.site.register(models.Appendices)
@admin.register(models.PaymentGateway)

class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = (
        'plan', 'user', 'amount', 'value', 'payment_id', 
        'code', 'create_date', 'name_status', 'status',
        'document', 'picture', 'send_farabours',
        'message_farabourse',
        'provided_finance_price_farabourse',
        'reference_number',
        'track_id',
        'card_number',
        'invoice',
        'service_code',
    )
    
    search_fields = (
        'plan__persian_name',
        'user',
        'payment_id',
        'code',
        'description',
        'track_id',

    )
    
    list_filter = (
        'status', 'create_date', 'send_farabours' , 'plan'
    )
    
    list_display_links = ('payment_id', 'code')
    
    list_editable = (
        'status', 'send_farabours'
    )
    
    list_per_page = 25
    ordering = ['-create_date']
    actions = ['export_as_excel', 'make_send_farabours_true', 'make_send_farabours_false']
    
    def export_as_excel(self, request, queryset):
        wb = Workbook()
        ws = wb.active
        ws.title = "پرداخت ها"

        headers = [
            'شناسه',
            'عنوان طرح',
            'کاربر',
            'مبلغ',
            'مقدار',
            'شناسه پرداخت',
            'توضیحات',
            'کد',
            'تاریخ ایجاد',
            'بیانیه ریسک',
            'وضعیت',
            'فیش',
            'ارسال به فرابورس',
            'کد پیگیری',
            'مبلغ پرداخت شده',
            'پیام فرابورس',
            'کد وضعیت پرداخت پاسارگاد',
            'شماره کارت',
            'نام کاربر',
            'کد سرویس',
            'شماره پیگیری',
            'کد وضعیت پرداخت پاسارگاد',
            'شماره کارت',
            'نام کاربر',
            'تاریخ فاکتور',
            'شماره فاکتور',
            'نام سرویس',
            'کد ارجاع شاپرک',
            'نام کاربر',
        ]
        ws.append(headers)

        for obj in queryset:
            row = [
                obj.id,
                obj.plan.persian_name if obj.plan else '',
                obj.user if obj.user else '',
                obj.amount,
                obj.value,
                obj.payment_id,
                obj.description,
                obj.code,
                remove_timezone(obj.create_date),
                obj.risk_statement,
                obj.name_status,
                obj.status,
                str(obj.document) if obj.document else '',
                str(obj.picture) if obj.picture else '',
                obj.send_farabours,
                obj.trace_code_payment_farabourse,
                obj.provided_finance_price_farabourse,
                obj.message_farabourse,
                obj.code_status_payment,
                obj.card_number,
                getattr(obj.admin, 'username', '') if hasattr(obj, 'admin') else '',
                obj.service_code,
                obj.track_id,
                obj.code_status_payment,
                obj.card_number,
                remove_timezone(obj.invoice_date),
                obj.invoice,
                obj.service_code,
                obj.reference_number,
                obj.name,
                obj.mobile,
            ]
            ws.append(row)

        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column_letter].width = adjusted_width

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=payments_{timezone.now().date()}.xlsx'

        wb.save(response)
        return response

    export_as_excel.short_description = "خروجی اکسل از موارد انتخاب شده"
    
    def make_send_farabours_true(self, request, queryset):
        queryset.update(send_farabours=True)
    make_send_farabours_true.short_description = "ارسال به فرابورس انجام شد"

    def make_send_farabours_false(self, request, queryset):
        queryset.update(send_farabours=False)
    make_send_farabours_false.short_description = "ارسال به فرابورس لغو شد"
    
    fieldsets = (
        ('اطلاعات پرداخت', {
            'fields': ('plan', 'user', 'amount', 'value', 'payment_id', 'description', 'code', 'create_date', 'risk_statement', 'name_status', 'status','track_id')
        }),
        ('اطلاعات فیش پرداخت', {
            'fields': ('document', 'picture')
        }),
        ('اطلاعات فرابورس', {
            'fields': ('send_farabours', 'trace_code_payment_farabourse', 'provided_finance_price_farabourse', 'message_farabourse')
        }),
    )
 
admin.site.register(models.Comment)
admin.site.register(models.PicturePlan)
admin.site.register(models.InformationPlan)
admin.site.register(models.EndOfFundraising)
admin.site.register(models.Warranty)
admin.site.register(models.Complaint)
