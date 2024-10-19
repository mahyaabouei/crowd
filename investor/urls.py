from django.urls import path
from.views import RequestViewset , DetailCartViewset , CartAdmin ,EvaluationCommitteeViewset,RiskCommitteeViewset,DetailCartAdminViewset,MessageAdminViewSet ,FinishCartViewset, MessageUserViewSet , AddInformationViewset , AddInfromationAdminViewset
from django.conf import settings

urlpatterns = [
    path('cart/', RequestViewset.as_view(), name='cart'),
    path('cart/', RequestViewset.as_view(), name='cart'),
    path('cart/detail/<int:id>/', DetailCartViewset.as_view(), name='cart-detail'),
    path('cart/admin/', CartAdmin.as_view(), name='cart-admin'),
    path('cart/admin/<int:id>/', CartAdmin.as_view(), name='cart-admin'),
    path('cart/detail/admin/<int:id>/', DetailCartAdminViewset.as_view(), name='cart-admin'),
    path('message/admin/<int:id>/', MessageAdminViewSet.as_view(), name='message-admin'),
    path('message/<int:id>/', MessageUserViewSet.as_view(), name='message-user'),
    path('addinformation/<int:id>/', AddInformationViewset.as_view(), name='add-information'),
    path('addinformation/admin/<int:id>/', AddInfromationAdminViewset.as_view(), name='add-information-admin'),
    path('update/finish/admin/<int:id>/', FinishCartViewset.as_view(), name='update-finish-admin'),
    path('update/risk/commitee/admin/<int:id>/', RiskCommitteeViewset.as_view(), name='update-risk-commitee-admin'),
    path('update/evaluation/commitee/admin/<int:id>/', EvaluationCommitteeViewset.as_view(), name='update-evaluation-commitee-admin'),
]
