from django.urls import path
from.views import ParticipationReportViewset,AuditReportViewset,ProgressReportViewset , DashBoardAdminViewset , DashBoardUserViewset , ProfitabilityReportViewSet


urlpatterns = [
    path('progres/report/admin/<str:trace_code>/', ProgressReportViewset.as_view(), name='progres-report-admin'),
    path('audit/report/admin/<str:trace_code>/', AuditReportViewset.as_view(), name='audit-report-admin'),
    path('participation/report/<str:trace_code>/', ParticipationReportViewset.as_view(), name='get-participation-report-user'),
    path('dashboard/admin/', DashBoardAdminViewset.as_view(), name='dashboard-admin'),
    path('dashboard/user/', DashBoardUserViewset.as_view(), name='dashboard-user'),
    path('report/admin/profitability/<str:trace_code>/', ProfitabilityReportViewSet.as_view(), name='profitability-report-admin'),
]