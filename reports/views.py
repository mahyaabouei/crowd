from django.shortcuts import render
from plan.models import Plan , PaymentGateway ,InformationPlan ,EndOfFundraising
from authentication.models import User , accounts , privatePerson
from investor.models import Cart
from .models import ProgressReport , AuditReport
from rest_framework.response import Response
from rest_framework import status 
from rest_framework.views import APIView
from authentication import fun
from .serializers import  ProgressReportSerializer ,AuditReportSerializer
from plan import serializers
from plan.CrowdfundingAPIService import CrowdfundingAPI 
from django.utils import timezone
from django.db.models import Sum
import pandas as pd
import datetime
from persiantools.jdatetime import JalaliDate
from authentication.serializers import accountsSerializer , privatePersonSerializer
from plan.views import get_name , get_account_number
import os
from django.conf import settings
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit   
from django.utils.decorators import method_decorator


# گزارش پیشرفت پروژه
# done
class ProgressReportViewset(APIView) :
    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post (self,request,trace_code) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:
            return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data.copy()
        serializer = ProgressReportSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if 'file' in request.FILES:
            serializer.uploaded_file = request.FILES['file']
        serializer.save(plan=plan)
        return Response (serializer.data, status=status.HTTP_200_OK)
    


    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get (self,request,trace_code) :
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:
            return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)
        progres_report = ProgressReport.objects.filter(plan=plan)
        if not progres_report.exists() :
            return Response({'error': 'progres report not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProgressReportSerializer(progres_report, many= True)
        return Response(serializer.data , status=status.HTTP_200_OK)


    @method_decorator(ratelimit(key='ip', rate='5/m', method='DELETE', block=True))
    def delete (self,request,trace_code) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        progres_report = ProgressReport.objects.filter(id=int(trace_code))
        if not progres_report.exists() :
            return Response({'error': 'progres report not found'}, status=status.HTTP_404_NOT_FOUND)
        progres_report.delete()
        return Response({'message':'succes'} , status=status.HTTP_200_OK)


# گزارش حسابررسی
# done
class AuditReportViewset(APIView) :
    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post (self,request,trace_code) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:
            return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data.copy()
        serializer =AuditReportSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if 'file' in request.FILES:
            serializer.uploaded_file = request.FILES
        serializer.save(plan=plan)
        return Response (serializer.data, status=status.HTTP_200_OK)
    


    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get (self,request,trace_code) :
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:
            return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)
        audit_report = AuditReport.objects.filter(plan=plan)
        if not audit_report.exists() :
            return Response({'error': 'audit report not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer =AuditReportSerializer(audit_report, many= True)
        return Response(serializer.data , status=status.HTTP_200_OK)


    @method_decorator(ratelimit(key='ip', rate='5/m', method='DELETE', block=True))
    def delete (self,request,trace_code) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        audit_report = AuditReport.objects.filter(id=int(trace_code))
        if not audit_report.exists() :
            return Response({'error': 'audit report not found'}, status=status.HTTP_404_NOT_FOUND)
        audit_report.delete()
        return Response({'message':'succes'} , status=status.HTTP_200_OK)


# گزارش مشارکت کننده ها
# done
class ParticipationReportViewset(APIView) :
    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get (self , request, trace_code) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:
            return Response({'error': 'plan not found'}, status=status.HTTP_404_NOT_FOUND)
        national_id =   user.uniqueIdentifier
        crowd_api = CrowdfundingAPI()
        participation = crowd_api.get_project_participation_report(trace_code , national_id)
        if participation.status_code != 200:
          return participation
        file_name = f"{trace_code}_{national_id}.pdf"
        file_path = os.path.join(settings.MEDIA_ROOT, 'reports', file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as pdf_file:
            pdf_file.write(participation.content)
        return Response({'url':f'/media/reports/{file_name}'},status=status.HTTP_200_OK)


# داشبورد ادمین 
# done
class DashBoardAdminViewset (APIView) : 
    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get (self , request) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        plan_all = Plan.objects.all().count()
        now = timezone.now()
        expire_plan = Plan.objects.filter(suggested_underwriting_end_date__lt=now).count()
        show_plan = InformationPlan.objects.filter(status_show=True).count()
        current_date = timezone.now().date()
        active_plan = Plan.objects.filter( suggested_underwriting_start_date__lte=current_date,suggested_underwriting_end_date__gte=current_date).count()
        cart_all = Cart.objects.all().count()
        expire_cart = Cart.objects.filter(finish_cart = True).count()
        active_cart = Cart.objects.filter(finish_cart = False).count()
        
        statics = {
            'all plan': plan_all,
            'expire plan': expire_plan,
            'active plan': active_plan,
            'show_plan': show_plan,
            'all cart': cart_all,
            'expire cart': expire_cart,
            'active cart': active_cart
            }
        
        tasks = []
        
        return Response (statics, status=status.HTTP_200_OK)
   


# داشبورد مشتری 
# done
class DashBoardUserViewset(APIView) :
    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get (self,request) : 
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()
        plan_all = Plan.objects.all().count()
        current_date = timezone.now().date()
        active_plan = Plan.objects.filter( suggested_underwriting_start_date__lte=current_date,suggested_underwriting_end_date__gte=current_date).count()
        payments = PaymentGateway.objects.filter(user=user.uniqueIdentifier).values('plan').distinct()

        end_of_fundraising = EndOfFundraising.objects.filter(plan__in = payments)
        end_of_fundraising_serializer = serializers.EndOfFundraisingSerializer(end_of_fundraising,many=True)
        date_profit = []
        for i in end_of_fundraising_serializer.data :
            date = i['date_operator']
            type = i['type']
            amount = i['amount_operator']
            plan = i['plan']
            date = datetime.datetime.strptime(date , '%Y-%m-%d')
            date_jalali = JalaliDate.to_jalali(date)
            date_jalali =str(date_jalali)
            date_profit.append({'type': type, 'date': date_jalali , 'amount': amount , 'plan' : plan})

        
        payments_count = payments.count()
        total_value = PaymentGateway.objects.filter(user=user.uniqueIdentifier).aggregate(total_value_sum=Sum('value'))['total_value_sum']
        if total_value is None:
            total_value = 0

        total_rate_of_return = InformationPlan.objects.filter(plan__in=payments).aggregate(total_rate_sum=Sum('rate_of_return'))['total_rate_sum']        
        if total_rate_of_return is None:
            total_rate_of_return = 0
        return Response ({'all plan' :plan_all , 'active plan' : active_plan , 'participant plan' :payments_count , 'total value' : total_value , 'all rate of return' :  total_rate_of_return  , 'profit' : date_profit}, status=status.HTTP_200_OK)
    
# گزارش سود دهی ادمین
class ProfitabilityReportViewSet(APIView) :
    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get(self,request,trace_code):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        if not trace_code:
            return Response({'error': 'trace_code not found'}, status=status.HTTP_400_BAD_REQUEST)
        plan =Plan.objects.filter(trace_code=trace_code)
        if not plan.exists():
            return Response({'error': 'plan not found'}, status=status.HTTP_404_NOT_FOUND)
        plan =plan.first()
        end_plan = EndOfFundraising.objects.filter(plan=plan,type=2)
        if not end_plan.exists():
            return Response({'error': 'plan not end'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        end_plan = serializers.EndOfFundraisingSerializer(end_plan,many=True)
        user_peyment = PaymentGateway.objects.filter(plan=plan,status='3')

        if not user_peyment :
            return Response({'error': 'payment not fund'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        user_peyment = serializers.PaymentGatewaySerializer(user_peyment,many=True)

        information = InformationPlan.objects.filter(plan=plan)
        if not information.exists():
            return Response({'error': 'information not fund'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        information_serializer = serializers.InformationPlanSerializer(information.first())

        rate_of_return = ((information_serializer.data['rate_of_return'])/100) /365
        df = pd.DataFrame(user_peyment.data)[['user','amount','value']].groupby(by=['user']).sum().reset_index()
        account_numbers = []
        user_names = []

        for i in df['user']:
            user_obj = User.objects.filter(uniqueIdentifier=i).first()
            if user_obj is not None:
                account_number = get_account_number(user_obj)
                user_name = get_name(user_obj)
            else:
                account_number = 'N/A' 
                user_name = 'N/A'
            
            account_numbers.append(account_number)
            user_names.append(user_name)
        df ['account_number'] = account_numbers
        df ['user_name'] = user_names

        pey_df = pd.DataFrame(end_plan.data).sort_values('date_operator')[['type','date_operator']]
        start_project = datetime.datetime.fromisoformat(information_serializer.data['payment_date']).replace(tzinfo=None)
        pey_df['date_operator'] = pd.to_datetime(pey_df['date_operator']).dt.tz_localize(None)
        pey_df['start_project'] = start_project
        pey_df['date_diff'] = (pey_df['date_operator'] - pey_df['start_project']).dt.days
        pey_df['date_diff'] = pey_df['date_diff'] - pey_df['date_diff'].shift(1).fillna(0)

        pey_df['profit'] = pey_df['date_diff'] * rate_of_return 
        pey_df = pey_df.sort_values('date_diff')
        qest = 1
        for i in pey_df.index : 
            df[f'profit{qest}'] = pey_df['profit'][i]
            df[f'value{qest}'] = pey_df['profit'][i] * df['value']
            df[f'date_operator{qest}'] = pey_df['date_operator'][i]
            qest += 1

        df = df.to_dict('records')
        return Response(df, status=status.HTTP_200_OK)
    