from django.urls import path
from.views import ParticipationReportViewset,AuditReportViewset,ProgressReportViewset , ProgressReportByIDViewset, DashBoardAdminViewset , AuditReportByIDViewset, DashBoardUserViewset , ProfitabilityReportViewSet , SendSmsFinishPlanViewset ,SendSmsStartPlanViewset , MarketReportViewset


urlpatterns = [
    path('progres/report/admin/<str:trace_code>/', ProgressReportViewset.as_view(), name='progres-report-admin-all'),
    path('progres/report/admin/<str:trace_code>/<int:id>/', ProgressReportViewset.as_view(), name='progres-report-admin'),
    path('audit/report/admin/<str:trace_code>/', AuditReportViewset.as_view(), name='audit-report-admin'),
    path('audit/report/admin/<str:trace_code>/<int:id>/', AuditReportViewset.as_view(), name='audit-report-admin-by-id'),
    path('participation/report/<str:trace_code>/', ParticipationReportViewset.as_view(), name='get-participation-report-user'),
    path('dashboard/admin/', DashBoardAdminViewset.as_view(), name='dashboard-admin'),
    path('dashboard/user/', DashBoardUserViewset.as_view(), name='dashboard-user'),
    path('report/admin/profitability/<str:trace_code>/', ProfitabilityReportViewSet.as_view(), name='profitability-report-admin'),
    path('send/sms/finish/plan/<str:trace_code>/', SendSmsFinishPlanViewset.as_view(), name='send-sms-finish-plan'),
    path('send/sms/start/plan/', SendSmsStartPlanViewset.as_view(), name='send-sms-start-plan'),
    path('progres/report/id/admin/', ProgressReportByIDViewset.as_view(), name='progress-report-admin-by-id'),
    path('progres/report/all/admin/', ProgressReportByIDViewset.as_view(), name='progress-report-admin-all'),
    path('audit/report/id/admin/', AuditReportByIDViewset.as_view(), name='audit-report-admin-by-id'),
    path('audit/report/all/admin/', AuditReportByIDViewset.as_view(), name='audit-report-admin-all'),
    path('market/report/admin/', MarketReportViewset.as_view(), name='market-report-admin'),
]
