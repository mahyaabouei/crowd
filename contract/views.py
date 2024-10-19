from django.shortcuts import render
from investor import models
from manager import models
from .models import SignatureCompany
from rest_framework import status 
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication import fun
from investor import serializers
from reportlab.pdfgen import canvas
import os
from django.conf import settings
from reportlab.lib.pagesizes import A4  
from reportlab.lib import colors
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from .utilti import ContarctCreator


# انتخاب مدیران شرکت برای حق امضا توسط ادمین
# done
class SignatureViewset (APIView):
    def post (self,request,id):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        cart = models.Cart.objects.filter(id=id).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        signature, created = SignatureCompany.objects.get_or_create(cart=cart)
        data = request.data
        signature_serializer = serializers.SignatureCompanySerializer(instance=signature, data=data)
        if signature_serializer.is_valid():
            signature_serializer.save()
            return Response(signature_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(signature_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

# فعال کردن وضعیت حق امضای مدیران مشتری توسط ادمین
# done
class SetSignatureViewset(APIView) :
    def post (self,request,id):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        cart = models.Cart.objects.filter(id=id).first()
        data = request.data.copy()
        manager_ids = data.get('ids', [])
        if not manager_ids or not isinstance(manager_ids, list):
            return Response({'error': 'Manager IDs must be provided as a list'}, status=status.HTTP_400_BAD_REQUEST)
        managers = models.Manager.objects.filter(cart=cart, id__in=manager_ids)
        if not managers.exists():
            return Response({'error': 'No matching managers found'}, status=status.HTTP_404_NOT_FOUND)
        managers.update(signature= True)  
        return Response ({'success': True}, status=status.HTTP_200_OK)
    
# لیست مدیران مشتری که حق امضای فعال دارند براساس کارت منتخب 
    def get(self,request,id) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        cart = models.Cart.objects.filter(id=id).first()
        manager = models.Manager.objects.filter(cart=cart)
        if not manager  :
            return Response ({'error':'manager not found'},status=self.HTTP_404_NOT_FOUND)
        manager_info = []
        
        for i in manager :
            if i.signature == True :
                manager_info.append({
                    'national_code': i.national_code,
                    'name': i.name,
                    'signature' : i.signature
                    }) 

        return Response ({'managers informations' :manager_info }, status=status.HTTP_200_OK)



# وارد کردن اطلاعات قرارداد عاملیت توسط ادمین
# done
class SetCartAdminViewset(APIView) :
    def post (self,request,id) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        cart = models.Cart.objects.filter(id=id).first()

        data = request.data.copy()

        
        update_fields = [
            'otc_fee', 'publication_fee', 'dervice_fee', 'design_cost',
            'percentage_total_amount', 'payback_period', 'swimming_percentage','lock_payback_period','lock_swimming_percentage',
            'partnership_interest', 'guarantee', 'role_141' , 'Prohibited', 'criminal_record','lock_partnership_interest',
            'effective_litigation' , 'bounced_check', 'non_current_debt', 'minimum_deposit_10', 'lock_contract','lock_guarantee'
        ]
        for i in update_fields:
            
            if i in data:
                setattr(cart, i, data.get(i))
        cart.save()
        serializer = serializers.CartSerializer(cart)
        
        return Response ({'success': True , 'cart' : serializer.data}, status=status.HTTP_200_OK)
    
    def get (self,request,id) : 
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        cart = models.Cart.objects.filter(id=id).values('otc_fee', 'publication_fee', 'dervice_fee', 'design_cost',
            'percentage_total_amount', 'payback_period', 'swimming_percentage','lock_swimming_percentage','lock_partnership_interest',
            'partnership_interest','lock_payback_period', 'guarantee', 'role_141' , 'Prohibited', 'criminal_record','lock_guarantee',
            'effective_litigation' , 'bounced_check', 'non_current_debt', 'minimum_deposit_10', 'lock_contract')
        if cart  :
            return Response(cart, status=status.HTTP_200_OK)
        return Response ({'error': 'not found'}, status=status.HTTP_404_NOT_FOUND)




# وارد کردن اطلاعات قرارداد عاملیت توسط مشتری
# done
class SetCartUserViewset(APIView) :
    def post (self,request,id) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()
        cart = models.Cart.objects.filter(id=id).first()

        data = request.data.copy()

        
        update_fields = [
            'otc_fee', 'publication_fee', 'dervice_fee', 'design_cost',
            'percentage_total_amount', 'payback_period', 'swimming_percentage',
            'partnership_interest', 'guarantee' , 'role_141' , 'Prohibited', 'criminal_record',
            'effective_litigation' , 'bounced_check', 'non_current_debt', 'minimum_deposit_10', 'lock_contract'
        ]

        for i in update_fields:
            if i in data:
                setattr(cart, i, data.get(i))
        cart.save()
        serializer = serializers.CartSerializer(cart)
        return Response ({'success': True , 'cart' : serializer.data}, status=status.HTTP_200_OK)



class PdfViewset(APIView) :
    def post(self, request,id):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()
        cart = models.Cart.objects.filter(id=id).first()
        if not cart:
            return Response ({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        contract = ContarctCreator(id)
        contract.Cover()
        url = contract.Save()
        return Response({'link': url}, status=status.HTTP_200_OK)

        # # ایجاد پوشه برای ذخیره فایل‌های PDF
        # pdf_folder = os.path.join(settings.MEDIA_ROOT, 'pdf')
        # os.makedirs(pdf_folder, exist_ok=True)
        # # نام فایل PDF
        # pdf_filename = f'cart-{cart.id}.pdf'
        # pdf_path = os.path.join(pdf_folder, pdf_filename)
        # try:
            # pdf_canvas = canvas.Canvas(pdf_path, pagesize=A4)
            # width, height = A4
            # font_path = os.path.join(settings.BASE_DIR, 'fonts', 'IRANSans.ttf')  
            # pdfmetrics.registerFont(TTFont('Persian', font_path))
            # pdf_canvas.setFont('Persian', 12)
            # # اضافه کردن متن به PDF
            # pdf_canvas.drawString(200, 750, text)
            # # کشیدن یک خط مشکی در کل عرض صفحه در 1/5 نهایی صفحه
            # pdf_canvas.setStrokeColor(colors.black)   # تنظیم ضخامت خط برای بولد کردن
            # pdf_canvas.setLineWidth(3)   
            # y_position = height * 0.2   # یک‌پنجم نهایی صفحه
            # pdf_canvas.line(0, y_position, width, y_position)    
            # # نوشتن متن "محل درج" بالای خط با معکوس کردن متن
            # place_text = "محل درج  مهر و امضا"
            # reshaped_place_text = arabic_reshaper.reshape(place_text)
            # bidi_place_text = get_display(reshaped_place_text)
            # pdf_canvas.drawString(450, y_position - 20, bidi_place_text) # خط کل عرض صفحه را پوشش می‌دهد

            # # اضافه کردن شماره صفحه در پایین صفحه با معکوس کردن متن
            # page_number_text = f"صفحه {pdf_canvas.getPageNumber()}"
            # reshaped_page_text = arabic_reshaper.reshape(page_number_text)
            # bidi_page_text = get_display(reshaped_page_text)
            # pdf_canvas.drawCentredString(width / 2, 15, bidi_page_text)  # شماره صفحه در پایین و مرکز صفحه
            # # ذخیره فایل PDF
            # pdf_canvas.save()

            # # ایجاد لینک فایل PDF
            # pdf_url = f'{settings.MEDIA_URL}pdf/{pdf_filename}'
            # return Response({'link': pdf_url}, status=status.HTTP_200_OK)

        # except Exception as e:
        #     return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

