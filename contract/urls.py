from django.urls import path
from.views import SignatureViewset , SetSignatureViewset , SetCartAdminViewset , SetCartUserViewset,PdfViewset
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('signature/<int:id>/', SignatureViewset.as_view(), name='signature-company'),
    path('setsignature/admin/<int:id>/', SetSignatureViewset.as_view(), name='set-signature-admin'),
    path('setcart/admin/<int:id>/', SetCartAdminViewset.as_view(), name='set-cart-admin'),
    path('setcart/<int:id>/', SetCartUserViewset.as_view(), name='set-cart-user'),
    path('pdf/<int:id>/', PdfViewset.as_view(), name='pdf'),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)