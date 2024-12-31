from django.urls import path
from.views import PlansViewset, BankReceiptViewset,CheckVerificationReceiptAdminViewset, WarrantyListAdminViewset,ComplaintViewset,CheckVerificationPaymentAdminViewset,PaymentUserReport ,SendParticipationNotificationViewset,PaymentInquiryViewSet,PlanViewset,PaymentUser, CertificateAdminViewset, Certificate,TransmissionViewset ,ParticipantMenuViewset,  DocumentationViewset,WarrantyAdminViewset,AppendicesViewset,PaymentDocument,EndOfFundraisingViewset,ShareholdersListExelViewset, SendParticipationCertificateToFaraboursViewset,CommentAdminViewset , CommentViewset ,InformationPlanViewset   ,SendpicturePlanViewset , ParticipantViewset 


urlpatterns = [

    path('plans/', PlansViewset.as_view(), name='plans'),
    path('plan/<str:trace_code>/', PlanViewset.as_view(), name='plan'),
    path('appendices/<str:trace_code>/', AppendicesViewset.as_view(), name='appendices-admin'),
    path('send/picture/<str:trace_code>/', SendpicturePlanViewset.as_view(), name='send-picture-admin'),
    path('documentation/<str:trace_code>/', DocumentationViewset.as_view(), name='documentation-admin'),
    path('comment/user/<str:trace_code>/', CommentViewset.as_view(), name='comment-user'),
    path('comment/admin/<str:trace_code>/', CommentAdminViewset.as_view(), name='comment-admin'),
    path('payment/document/<str:trace_code>/', PaymentDocument.as_view(), name='payment-admin'), # مشخصات سرمایه گذران 
    path('payment/document/user/<str:trace_code>/', PaymentUserReport.as_view(), name='payment-user'), # مشخصات سرمایه گذر کاربران برای کاربر 
    path('payment/user/<str:trace_code>/', PaymentUser.as_view(), name='payment-user'),
    path('certificate/user/<str:trace_code>/', Certificate.as_view(), name='participant-user'),
    path('participant/user/<str:trace_code>/', ParticipantViewset.as_view(), name='participant-user'),   # ???
    path('information/plan/admin/<str:trace_code>/', InformationPlanViewset.as_view(), name='add-information-plan-admin'),
    path('end/fundraising/admin/<str:trace_code>/', EndOfFundraisingViewset.as_view(), name='end-fundraising-plan-admin'),
    path('send/participation/certificate/farabours/admin/<str:trace_code>/', SendParticipationCertificateToFaraboursViewset.as_view(), name='send-participation-certificate-farabours-admin'),
    path('read/exel/shareholder/admin/<str:key>/', ShareholdersListExelViewset.as_view(), name='exel-shareholders-admin'),
    path('warranty/admin/<str:key>/', WarrantyAdminViewset.as_view(), name='warranty-admin'), #  ضمانت نامه
    path('warranty/admin/', WarrantyAdminViewset.as_view(), name='warranty-admin'), #  ضمانت نامه
    path('warranty/list/admin/', WarrantyListAdminViewset.as_view(), name='warranty-admin'), #  ضمانت نامه لیست
    path('transmission/user/<str:key>/', TransmissionViewset.as_view(), name='transmission-user'), # درگاه پرداخت
    path('bank/reciept/payment/admin/<int:id>/', BankReceiptViewset.as_view(), name='bank-reciept-payment-admin'), # فیش بانکی های ادمین
    path('participant/menu/user/', ParticipantMenuViewset.as_view(), name='participant-menu-user'), # گواهی مشارکت 
    path('certificate/admin/<str:trace_code>/', CertificateAdminViewset.as_view(), name='certificate-admin'), #  گواهی مشارکت  ادمین
    path('payment/inquiry/admin/<str:trace_code>/', PaymentInquiryViewSet.as_view(), name='payment-inquiry-admin'), #چک پرداخت های درگاه بانکی
    path('send/participation/notification/admin/<str:trace_code>/', SendParticipationNotificationViewset.as_view(), name='send-participation-notification-admin'), # اعلام تکمیل طرح از طرف ادمین
    path('check/verification/payment/admin/', CheckVerificationPaymentAdminViewset.as_view(), name='check-verification-payment-admin'), # بررسی پرداخت چک های سود سرمایه پذیر از طرف ادمین    
    path('check/verification/receipt/admin/', CheckVerificationReceiptAdminViewset.as_view(), name='check-verification-receipt-admin'), # بررسی دریافت چک های سود سرمایه گذار از طرف ادمین    
    path('complaint/user/<str:trace_code>/', ComplaintViewset.as_view(), name='complaint'), # شکایات کاربران
]

