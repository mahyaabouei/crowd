import os
import django
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crowd.settings")
django.setup()

apps = settings.INSTALLED_APPS

app_list = [app for app in apps if not app.startswith('django.contrib')]

for app in app_list:
    print(f"Running makemigrations for {app}...")
    os.system(f"python manage.py makemigrations {app}")
