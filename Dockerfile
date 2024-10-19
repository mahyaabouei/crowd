# استفاده از تصویر پایه
FROM python:3.12

# تنظیم پوشه کاری
WORKDIR /app

# کپی کردن فایل‌های پروژه به داخل کانتینر
COPY . /app

# نصب وابستگی‌ها
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install GuardPyCaptcha

# اعمال تنظیمات محیطی برای Django
ENV DJANGO_SETTINGS_MODULE=crowd.settings
ENV PYTHONUNBUFFERED=1

# اجرای Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "crowd.wsgi:application"]
