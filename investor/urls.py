from django.urls import path
from.views import RequestViewset , DetailCartViewset , CartAdmin ,EvaluationCommitteeViewset,RiskCommitteeViewset,DetailCartAdminViewset,MessageAdminViewSet ,FinishCartViewset, MessageUserViewSet , AddInformationViewset , AddInfromationAdminViewset
from django.conf import settings

urlpatterns = [
    path('cart/', RequestViewset.as_view(), name='cart'),
    path('cart/', RequestViewset.as_view(), name='cart'),
    path('cart/detail/<str:unique_id>/', DetailCartViewset.as_view(), name='cart-detail'),
    path('cart/admin/', CartAdmin.as_view(), name='cart-admin'),
    path('cart/admin/<str:unique_id>/', CartAdmin.as_view(), name='cart-admin'),
    path('cart/detail/admin/<str:unique_id>/', DetailCartAdminViewset.as_view(), name='cart-admin'),
    path('message/admin/<str:unique_id>/', MessageAdminViewSet.as_view(), name='message-admin'),
    path('message/<str:unique_id>/', MessageUserViewSet.as_view(), name='message-user'),
    path('addinformation/<str:unique_id>/', AddInformationViewset.as_view(), name='add-information'),
    path('addinformation/admin/<str:unique_id>/', AddInfromationAdminViewset.as_view(), name='add-information-admin'),
    path('update/finish/admin/<str:unique_id>/', FinishCartViewset.as_view(), name='update-finish-admin'),
    path('update/risk/commitee/admin/<str:unique_id>/', RiskCommitteeViewset.as_view(), name='update-risk-commitee-admin'),
    path('update/evaluation/commitee/admin/<str:unique_id>/', EvaluationCommitteeViewset.as_view(), name='update-evaluation-commitee-admin'),
]
