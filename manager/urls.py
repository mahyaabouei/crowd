from django.urls import path
from.views import ManagerViewset , ManagerAdminViewset , ResumeViewset , ResumeAdminViewset , ShareholderViewset , ShareholderAdminViewset , ValidationViewset , ValidationAdminViewset , HistoryViewset , HistoryAdminViewset 


urlpatterns = [
    path('manager/<str:unique_id>/', ManagerViewset.as_view(), name='manager'),
    path('manager/', ManagerViewset.as_view(), name='manager-list'),
    path('manager/admin/', ManagerAdminViewset.as_view(), name='manager-list-admin'),
    path('manager/admin/<str:unique_id>/', ManagerAdminViewset.as_view(), name='manager-update-admin'),
    path('resume/<str:unique_id>/', ResumeViewset.as_view(), name='resume'),
    path('resume/admin/<str:unique_id>/', ResumeAdminViewset.as_view(), name='resume-admin'),
    path('shareholder/<str:unique_id>/', ShareholderViewset.as_view(), name='shareholder'),
    path('shareholder/admin/<str:unique_id>/', ShareholderAdminViewset.as_view(), name='shareholder-admin'),
    path('validation/<str:unique_id>/', ValidationViewset.as_view(), name='validation'),
    path('validation/admin/<str:unique_id>/', ValidationAdminViewset.as_view(), name='validation-admin'),
    path('history/<str:unique_id>/', HistoryViewset.as_view(), name='history'),
    path('history/admin/<str:unique_id>/', HistoryAdminViewset.as_view(), name='history-admin'),
]