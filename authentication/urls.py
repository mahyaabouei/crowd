from django.urls import path
from.views import CaptchaViewset,OtpViewset,LoginViewset,OtpAdminViewset,UserOneViewset,LogoutViewset,AddBoursCodeUserViewset,LoginAdminViewset , InformationViewset, UserListViewset , OtpUpdateViewset, UpdateInformationViewset

urlpatterns = [
    path('captcha/', CaptchaViewset.as_view(), name='captcha'),
    path('otp/', OtpViewset.as_view(), name='otp'),
    path('login/', LoginViewset.as_view(), name='login'),
    path('information/', InformationViewset.as_view(), name='information'),
    path('otp/admin/', OtpAdminViewset.as_view(), name='otp-admin'),
    path('login/admin/', LoginAdminViewset.as_view(), name='login-admin'),
    path('listuser/admin/', UserListViewset.as_view(), name='list-user-admin'),
    path('otp/update/', OtpUpdateViewset.as_view(), name='otp-update-profile'),
    path('update/profile/', UpdateInformationViewset.as_view(), name='update-profile'),
    path('add/bours/code/user/', AddBoursCodeUserViewset.as_view(), name='add-bours-code-user'),
    path('log/out/', LogoutViewset.as_view(), name='log-out'),
]