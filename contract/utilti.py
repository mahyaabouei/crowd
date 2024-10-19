from reportlab.pdfgen import canvas
import os
from django.conf import settings
from reportlab.lib.pagesizes import A4  
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from investor.models import Cart
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib import colors
from persiantools.jdatetime import JalaliDate
import datetime
import random


def date_str_to(date):
    return date.strftime("%Y-%m-%d")  

def date_to_jalali(date):
    return JalaliDate(date)
random_number = random.randint(100, 999)

class ContarctCreator():
    def __init__(self,id):
        self.id = id
        pdf_folder = os.path.join(settings.MEDIA_ROOT, 'pdf')
        
        os.makedirs(pdf_folder, exist_ok=True)
        pdf_filename = f'cart-{id}.pdf'
        font_path = os.path.join(settings.BASE_DIR, 'fonts', 'IRANSans.ttf')
        pdf_path = os.path.join(pdf_folder, pdf_filename)
        pdfmetrics.registerFont(TTFont('Persian', font_path))
        self.pdf_canvas = canvas.Canvas(pdf_path, pagesize=A4)
        MEDIA_URL = settings.MEDIA_URL
        self.download_link = f'{MEDIA_URL}pdf/{pdf_filename}'
    
    def information(self):
        return Cart.objects.filter(id=self.id).first()


    def text(self,text,position='center',y=0,size=12, color=colors.black):
        text = arabic_reshaper.reshape(text)
        text = get_display(text)
        self.pdf_canvas.setFont('Persian', size)
        self.pdf_canvas.setFillColor(color)  
        text_width = self.pdf_canvas.stringWidth(text, 'Persian', size)

        page_width = A4[0]
        if position=='center':
          x = (page_width - text_width) / 2
        else:
          x = 0
        return x, y, text
    
    def add_image(self, image_path, x, y, width=None, height=None):
        """Add image to PDF at specified position"""
        if os.path.exists(image_path):
            self.pdf_canvas.drawImage(image_path, x, y, width=width, height=height)
        else:
            print(f"Image not found: {image_path}")


    def Cover(self):
        company = Cart.objects.get(id=self.id)
        company_name = company.company_name
        base_text = f'قرارداد عاملیت شرکت {company_name}'
        x, y, text = self.text(base_text,y=800)
        self.pdf_canvas.drawString(x, y, text)

        kind = str(str(company.company_kind).replace('1', 'سهامی عام').replace('2', 'با مسئولیت محدود').replace('3', 'تضامنی').replace('4', 'مختلط').replace('5', 'نسبی').replace('6', 'تعاونی').replace('7', 'دانش بنیان').replace('8', 'سهامی خاص'))
        x, y, text = self.text(f'({kind})',y=775, size=10,color=colors.gray)
        self.pdf_canvas.drawString(x, y, text)

        if company.logo:
            self.add_image(company.logo.path, 100, 600, width=150, height=150)  # Adjust path and position
        self.add_image('media/static/logo/sabadlogo.png' , 350 , 600, width=120, height=120)

        current_date = datetime.datetime.now()
        jalali_date = date_to_jalali(current_date) 
        contract_year = jalali_date.year
        contract_month = jalali_date.month
        contract_number = f'{contract_year}/{contract_month}/{self.id}/{random_number}'
        x, y, text = self.text(f'شماره قرارداد: {contract_number}', y=550, size=12)
        self.pdf_canvas.drawString(x, y, text)
        
        contract_date = company.creat
        contract_date = date_to_jalali(contract_date) 
        contract_date = contract_date.strftime('%Y/%m/%d')
        x, y, text = self.text(f'تاریخ قرارداد: {contract_date}', y=500, size=12)
        self.pdf_canvas.drawString(x, y, text)


    def Save(self):
        self.pdf_canvas.save()
        return self.download_link










