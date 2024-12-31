from django.shortcuts import render
from plan.models import Plan , PaymentGateway ,InformationPlan ,EndOfFundraising , ProjectOwnerCompan
from authentication.models import User ,addresses , privatePerson
from investor.models import Cart
from .models import ProgressReport , AuditReport
from rest_framework.response import Response
from rest_framework import status 
from rest_framework.views import APIView
from authentication import fun
from .serializers import  ProgressReportSerializer ,AuditReportSerializer
from plan.serializers import PaymentGatewaySerializer
from plan import serializers
from plan.CrowdfundingAPIService import CrowdfundingAPI 
from django.utils import timezone
from django.db.models import Sum
import pandas as pd
import datetime
from persiantools.jdatetime import JalaliDate
from plan.views import get_name , get_account_number
import os
from django.conf import settings
from django_ratelimit.decorators import ratelimit   
from django.utils.decorators import method_decorator
from utils.user_notifier import UserNotifier
from authentication.models import accounts
# گزارش پیشرفت پروژه
# done
class ProgressReportViewset(APIView) :
    @method_decorator(ratelimit(**settings.RATE_LIMIT['PATCH']), name='patch')
    def patch (self,request,trace_code,id) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:
            return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)
        progres_report = ProgressReport.objects.filter(plan=plan,id=id).first()
        if not progres_report:
            return Response({'error': 'Progress report not found'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data.copy()
        serializer = ProgressReportSerializer(progres_report,data=data,partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if 'file' in request.FILES:
            serializer.uploaded_file = request.FILES['file']
        serializer.save(plan=plan)
        return Response (serializer.data, status=status.HTTP_200_OK)
    


    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get (self,request,trace_code) :
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:
            return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)
        progres_report = ProgressReport.objects.filter(plan=plan)
        if not progres_report.exists() :
            return Response([], status=status.HTTP_200_OK)
        serializer = ProgressReportSerializer(progres_report, many= True)
        return Response(serializer.data , status=status.HTTP_200_OK)


# گزارش حسابررسی
# done
class AuditReportViewset(APIView) :
    @method_decorator(ratelimit(**settings.RATE_LIMIT['PATCH']), name='patch')
    def patch (self,request,trace_code,id) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:
            return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)
        audit_report = AuditReport.objects.filter(plan=plan,id=id).first()
        if not audit_report:
            return Response({'error': 'Audit report not found'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data.copy()
        serializer =AuditReportSerializer(audit_report,data=data,partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if 'file' in request.FILES:
            serializer.uploaded_file = request.FILES['file']
        serializer.save(plan=plan)
        return Response (serializer.data, status=status.HTTP_200_OK)
    

    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get (self,request,trace_code) :
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:
            return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)
        audit_report = AuditReport.objects.filter(plan=plan)
        if not audit_report.exists() :
            return Response([], status=status.HTTP_200_OK)
        serializer =AuditReportSerializer(audit_report, many= True)
        return Response(serializer.data , status=status.HTTP_200_OK)
       

# گزارش مشارکت کننده ها
# done
class ParticipationReportViewset(APIView) :
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get (self , request, trace_code) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_401_UNAUTHORIZED)
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
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get (self , request) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        plan_all = Plan.objects.all().count()
        now = timezone.now()
        expire_plan = Plan.objects.filter(suggested_underwriting_end_date__lt=now).count()
        show_plan = InformationPlan.objects.filter(status_show=True).count()
        active_plan = InformationPlan.objects.filter(status_second='1')
        active_plan = active_plan.values('plan').distinct().count()
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
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get (self,request) : 
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_401_UNAUTHORIZED)
        user = user.first()
        plan_all = Plan.objects.all()
        information_plan = InformationPlan.objects.filter(plan__in = plan_all , status_show = True)
        plan_all = information_plan.count()
        active_plan = information_plan.filter(status_second = '1').count()
        payments = PaymentGateway.objects.filter(user=user.uniqueIdentifier , status='3').values('plan').distinct()
        end_of_fundraising = EndOfFundraising.objects.filter(plan__in = payments)
        end_of_fundraising_serializer = serializers.EndOfFundraisingSerializer(end_of_fundraising,many=True)
        date_profit = []
        for i in end_of_fundraising_serializer.data :
            date = i['date_operator']
            type = i['type']
            plan_id = i['plan']
            plan_name = Plan.objects.filter(id=plan_id).first()
            if plan_name:
                plan_name = plan_name.persian_name
            else:
                plan_name = ''
    
            try:
                plan_obj = Plan.objects.get(id=plan_id)
                plan_total = plan_obj.total_price
                if plan_obj.trace_code != 'e7e79c55-f89a-47d7-89f9-2d3c6a1e9de8' and type == '2':
                    amount = i['amount_operator'] /0.9
                else:
                    amount = i['amount_operator']
            except Plan.DoesNotExist:
                amount = None
                plan_total = None
            payment_value = PaymentGateway.objects.filter(user=user.uniqueIdentifier, status='3', plan=plan_id).aggregate(total_value_sum=Sum('value'))['total_value_sum'] or 0

            if type == '1':
                amount_end = payment_value
            else:
                if amount and plan_total:
                    amount_end = (amount/plan_total) * payment_value
                    amount_end = int(amount_end)
                else:
                    amount_end = 0
            date = datetime.datetime.strptime(date , '%Y-%m-%d')
            date_jalali = JalaliDate.to_jalali(date)
            date_jalali =str(date_jalali)
            date_profit.append({'type': type, 'date': date_jalali , 'amount': amount_end , 'plan' : plan_id, 'plan_name':plan_name, 'trace_code':plan_obj.trace_code})
            
        
        payments_count = payments.count()
        total_value =0
        payments_user = PaymentGateway.objects.filter(user=user.uniqueIdentifier ,  status = '3')
        for i in payments_user:
            if i.status == '3':
                total_value += i.value
        


        #total_rate_of_return
        peyment_user = PaymentGateway.objects.filter(user=user.uniqueIdentifier , status='3')
        total_rate_of_return = 0
        for i in peyment_user:
            rate_of_return = InformationPlan.objects.filter(plan=i.plan).first()
            total_rate_of_return += ((rate_of_return.rate_of_return / 100) * i.value)

        if total_rate_of_return is None:
            total_rate_of_return = 0

        referral_count = User.objects.filter(referal=user.uniqueIdentifier).exclude(uniqueIdentifier=user.uniqueIdentifier).count()

                
        return Response ({'all plan' :plan_all , 'active plan' : active_plan , 'participant plan' :payments_count , 'total value' : total_value , 'all rate of return' :  total_rate_of_return  , 'profit' : date_profit , 'referral count' : referral_count }, status=status.HTTP_200_OK)


# گزارش سود دهی ادمین
class ProfitabilityReportViewSet(APIView) :
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get(self,request,trace_code):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        if not trace_code:
            return Response({'error': 'trace_code not found'}, status=status.HTTP_400_BAD_REQUEST)
        plan =Plan.objects.filter(trace_code=trace_code)
        if not plan.exists():
            return Response({'error': 'plan not found'}, status=status.HTTP_404_NOT_FOUND)
        plan =plan.first()
        project_owner = ProjectOwnerCompan.objects.filter(plan=plan).first()
        if not project_owner:
            return Response({'error': 'project owner not found'}, status=status.HTTP_404_NOT_FOUND)
        project_owner_national_id = project_owner.national_id
        end_plan = EndOfFundraising.objects.filter(plan=plan,type=2)
        if not end_plan.exists():
            return Response({'error': 'plan not end'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        end_plan = serializers.EndOfFundraisingSerializer(end_plan,many=True)
        user_peyment = PaymentGateway.objects.filter(plan=plan, status='3').exclude(user=project_owner_national_id)

        if not user_peyment :
            return Response({'error': 'payment not fund'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        user_peyment = serializers.PaymentGatewaySerializer(user_peyment,many=True)

        information = InformationPlan.objects.filter(plan=plan)
        if not information.exists():
            return Response({'error': 'information not fund'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        information_serializer = serializers.InformationPlanSerializer(information.first())
        days_of_year = 365
        payment_date = information_serializer.data['payment_date']
        payment_date = datetime.datetime.strptime(payment_date, '%Y-%m-%dT%H:%M:%S%z')
        payment_date = JalaliDate.to_jalali(payment_date)
        payment_date = payment_date.year + 1

        pey_df = pd.DataFrame(end_plan.data).sort_values('date_operator')[['type','date_operator']]

        if payment_date % 4 == 0 and (payment_date % 100 != 0 or payment_date % 400 == 0):
            days_of_year = 366
        
        days = days_of_year
        rate_of_return = float(information_serializer.data['rate_of_return'])
        rate_of_return = ((rate_of_return)/100) /days
        df = pd.DataFrame(user_peyment.data)[['user','amount','value']].groupby(by=['user']).sum().reset_index()
        account_numbers = []
        user_names = []
        user_mobiles = []
        for i in df['user']:
            user_obj = User.objects.filter(uniqueIdentifier=i).first()
            if user_obj is not None:
                account_number = get_account_number(user_obj.uniqueIdentifier)
                user_name = get_name(user_obj.uniqueIdentifier)
                user_mobile = user_obj.mobile
            else:
                account_number = 'N/A' 
                user_name = 'N/A'
                user_mobile = 'N/A'
            account_numbers.append(account_number)
            user_names.append(user_name)
            user_mobiles.append(user_mobile)
        df ['account_number'] = account_numbers
        df ['user_name'] = user_names
        df ['user_mobile'] = user_mobiles
        
        # تبدیل start_project به Timestamp
        start_project = pd.Timestamp(datetime.datetime.fromisoformat(information_serializer.data['payment_date']).replace(tzinfo=None).date())
        pey_df['date_operator'] = pd.to_datetime(pey_df['date_operator']).dt.tz_localize(None)
        pey_df['start_project'] = start_project
        pey_df['date_diff'] = (pey_df['date_operator'] - pey_df['start_project']).dt.days
        pey_df['date_diff'] = pey_df['date_diff'] - pey_df['date_diff'].shift(1).fillna(0)

        if information_serializer.data['payback_period'] == '2':
            pey_df['profit'] = float(information_serializer.data['rate_of_return'])
        else:
            pey_df['profit'] = pey_df['date_diff'] * rate_of_return 

        qest = 1
        for i in pey_df.index : 
            df[f'profit{qest}'] = pey_df['profit'][i]

            df[f'value{qest}'] = pey_df['profit'][i] * df['value']
            df[f'value{qest}'] = df[f'value{qest}'].apply(lambda x: round(x, 0))
            df[f'date_operator{qest}'] = pey_df['date_operator'][i]
            qest += 1

        df = df.to_dict('records')
        return Response(df, status=status.HTTP_200_OK)
    

class SendSmsFinishPlanViewset(APIView) :
    @method_decorator(ratelimit(**settings.RATE_LIMIT['POST']), name='post')
    def post(self,request,trace_code) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        plans = Plan.objects.filter(trace_code=trace_code)
        if not plans.exists():
            return Response({'error': 'plan not found'}, status=status.HTTP_404_NOT_FOUND)
        plans = plans.first()
        payment_gateway = PaymentGateway.objects.filter(plan=plans,status='3' , send_farabours = True)
        if not payment_gateway.exists():
            return Response({'error': 'payment not found'}, status=status.HTTP_404_NOT_FOUND)
        unique_users = set()
        for i in payment_gateway:
            user = i.user
            if user in unique_users:
                continue
            unique_users.add(user)
            user = User.objects.filter(uniqueIdentifier=user).first()
            if not user:
                return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
            
            mobile = user.mobile
            address = addresses.objects.filter(user=user).first()
            email = address.email
            user_notifier = UserNotifier(mobile,email)
            user_notifier.send_finance_completion_sms()
            user_notifier.send_finance_completion_email()
        return Response({'message': 'sms sent'}, status=status.HTTP_200_OK)


class SendSmsStartPlanViewset(APIView) :
    @method_decorator(ratelimit(**settings.RATE_LIMIT['POST']), name='post')
    def post(self,request) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        user = User.objects.all()
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        for i in user:
            mobile = i.mobile
            address = addresses.objects.filter(user=i)
            for j in address:
                if not j:
                    return Response({'error': 'address not found'}, status=status.HTTP_404_NOT_FOUND)
                email = j.email
            data = request.data
            if data ['email'] is True :
                if data ['subject'] is None or data ['message'] is None:
                    return Response({'error': 'subject or message not found'}, status=status.HTTP_400_BAD_REQUEST)
                
                user_notifier = UserNotifier(mobile,email)
                user_notifier.send_sms(data['message'])
                user_notifier.send_email(data['subject'],data['message'])
            else:
                if data ['message'] is None:
                    return Response({'error': 'message not found'}, status=status.HTTP_400_BAD_REQUEST)
                user_notifier = UserNotifier(mobile,email)
                user_notifier.send_sms(data['message'])
        return Response({'message': 'sms sent'}, status=status.HTTP_200_OK)
        

class ProgressReportByIDViewset(APIView) :
    @method_decorator(ratelimit(**settings.RATE_LIMIT['PATCH']), name='patch')
    def patch (self,request) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        id = request.data.get('id')
        progres_report = ProgressReport.objects.filter(id=id).first()
        if not progres_report:
            return Response({'error': 'Progress report not found'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data.copy()
        serializer = ProgressReportSerializer(progres_report,data=data,partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if 'file' in request.FILES:
            serializer.uploaded_file = request.FILES['file']
        serializer.save()
        return Response (serializer.data, status=status.HTTP_200_OK)
    

    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get (self,request) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        progres_report = ProgressReport.objects.all()
        if not progres_report.exists() :
            return Response([], status=status.HTTP_200_OK)
        serializer = ProgressReportSerializer(progres_report, many= True)
        for i in serializer.data :
            plan = i['plan']['persian_suggested_symbol']
            date = i['date']
            date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
            date = JalaliDate.to_jalali(date)
            i['date'] = str(date)
            i['plan'] = plan
        return Response(serializer.data , status=status.HTTP_200_OK)


class AuditReportByIDViewset(APIView) :
    @method_decorator(ratelimit(**settings.RATE_LIMIT['PATCH']), name='patch')
    def patch (self,request) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        id = request.data.get('id')
        audit_report = AuditReport.objects.filter(id=id).first()
        if not audit_report:
            return Response({'error': 'Audit report not found'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data.copy()
        serializer =AuditReportSerializer(audit_report,data=data,partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if 'file' in request.FILES:
            serializer.uploaded_file = request.FILES['file']
        serializer.save()
        return Response (serializer.data, status=status.HTTP_200_OK)
    

    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get (self,request) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        
        audit_report = AuditReport.objects.all()
        if not audit_report.exists() :
            return Response([], status=status.HTTP_200_OK)
        
        serializer =AuditReportSerializer(audit_report, many= True)
        for i in serializer.data :
            plan = i['plan']['persian_suggested_symbol']
            date = i['date']
            date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
            date = JalaliDate.to_jalali(date)
            i['date'] = str(date)
            i['plan'] = plan
        return Response(serializer.data , status=status.HTTP_200_OK)
    
    

class MarketReportViewset(APIView) :
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get(self, request):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        
        market_report = PaymentGateway.objects.filter(status='3')
        if not market_report.exists():
            return Response([], status=status.HTTP_200_OK)
            
        serializer = PaymentGatewaySerializer(market_report, many=True)
        df = []
        
        for payment in serializer.data:
            user = User.objects.filter(uniqueIdentifier=payment['user']).first()
            if not user:
                continue
            user_name = get_name(user.uniqueIdentifier)
            if not user_name:
                user_name = 'N/A'
                

            # Check if user has valid referal
            if not user.referal or user.referal == '' or user.referal == 'None' or user.referal == payment['user']:
                continue

            marketer = User.objects.filter(uniqueIdentifier=user.referal).first()
            if not marketer:
                marketer_name = 'N/A'
                account = 'N/A'
            else:
                marketer_name = get_name(marketer.uniqueIdentifier)
                account = get_account_number(marketer.uniqueIdentifier)
            
            plan = Plan.objects.filter(id=payment['plan']).first()
            if not plan:
                plan = 'N/A'


            dic = {
                'user': user_name,
                'uniqueIdentifier': user.uniqueIdentifier,
                'plan': plan.persian_suggested_symbol,
                'value': payment['value'],
                'referal_code': user.referal,
                'marketer': marketer_name,
                'account': account,
            }
            df.append(dic)

        return Response(df, status=status.HTTP_200_OK)

