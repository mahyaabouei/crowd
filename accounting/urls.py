from django.urls import path
from .views import WalletAdminViewset , WalletAdmin2Viewset , WalletViewset  , TransactionAdminViewset ,TransactionAdmin2Viewset , Transaction2Viewset , TransactionViewset


urlpatterns = [
    path('wallet/admin/', WalletAdminViewset.as_view(), name='wallet-admin'),
    path('wallet/admin/<int:id>/', WalletAdmin2Viewset.as_view(), name='wallet-admin'),
    path('wallet/' , WalletViewset.as_view() , name='wallet-user'),
    path('transaction/admin/', TransactionAdminViewset.as_view(), name='transaction-admin'),
    path('transaction/admin/<int:id>/' , TransactionAdmin2Viewset.as_view() , name='wallet-admin'),
    path('transaction/', TransactionViewset.as_view(), name='transaction-user'),
    path('transaction/<int:id>/' , Transaction2Viewset.as_view() , name='wallet-user'),
]
