import datetime
from rest_framework.response import Response
from rest_framework import status 
from django.utils import timezone


def get_date_from_request(request, national_code):
    timestamp_key = f'{national_code}_date'
    if timestamp_key not in request.data:
        return None, f'Date for manager with national code {national_code} is missing'
    
    try:
        timestamp = int(request.data[timestamp_key]) / 1000
        date = timezone.make_aware(datetime.datetime.fromtimestamp(timestamp))
        return date, None
    except (ValueError, KeyError):
        return None, f'Invalid date format for manager {national_code}'