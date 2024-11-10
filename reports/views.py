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
from plan.views import get_name , get_account_number
import os
from django.conf import settings
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit   
from django.utils.decorators import method_decorator



class ProgressReportViewset(APIView):
    """
    This view allows an admin to upload a progress report associated with a specific plan, identified by its trace code.
    """

    @method_decorator(ratelimit(key='ip', rate='20/m', method='POST', block=True))
    def post(self, request, trace_code):
        """
        Upload a progress report for a specific plan.

        This method authenticates the admin using the Authorization header and allows them to upload a 
        progress report associated with a plan identified by its trace code.

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - If the plan with the specified trace code does not exist, an error is returned.
        - If the request data or file upload is invalid, an error is returned.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - trace_code (str, path): Unique trace code identifier for the plan.
            - report_data (dict, body): Data fields for the progress report.
            - file (file, body, optional): File to be attached to the progress report.

        Responses:
            200: {
                "id": <report_id>,
                "plan": <plan_id>,
                "uploaded_file": <file_url>,
                ...
            }
            400: {"error": "Authorization header is missing" / "Invalid data"}
            401: {"error": "admin not found"}
            404: {"error": "Plan not found"}
        """
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
        """
        Retrieve all progress reports for a specific plan by trace code.

        This method fetches all progress reports associated with a plan identified by its trace code.

        - If the plan with the specified trace code does not exist, an error is returned.
        - If no progress reports are associated with the plan, an error is returned.

        Parameters:
            - trace_code (str, path): Unique trace code identifier for the plan.

        Responses:
            200: [
                {
                    "id": <report_id>,
                    "plan": <plan_id>,
                    "uploaded_file": <file_url>,
                    ...
                },
                ...
            ]
            404: {"error": "Plan not found" / "progress report not found"}
        """
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


class AuditReportViewset(APIView):
    """
    This view allows an admin to upload an audit report associated with a specific plan, identified by its trace code.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request, trace_code):
        """
        Upload an audit report for a specific plan.

        This method authenticates the admin using the Authorization header and allows them to upload an 
        audit report associated with a plan identified by its trace code.

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - If the plan with the specified trace code does not exist, an error is returned.
        - If the request data or file upload is invalid, an error is returned.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - trace_code (str, path): Unique trace code identifier for the plan.
            - audit_data (dict, body): Data fields for the audit report.
            - file (file, body, optional): File to be attached to the audit report.

        Responses:
            200: {
                "id": <report_id>,
                "plan": <plan_id>,
                "uploaded_file": <file_url>,
                ...
            }
            400: {"error": "Authorization header is missing" / "Invalid data"}
            404: {"error": "admin not found" / "Plan not found"}
        """
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
        """
        Retrieve all audit reports for a specific plan by trace code.

        This method fetches all audit reports associated with a plan identified by its trace code.

        - If the plan with the specified trace code does not exist, an error is returned.
        - If no audit reports are associated with the plan, an error is returned.

        Parameters:
            - trace_code (str, path): Unique trace code identifier for the plan.

        Responses:
            200: [
                {
                    "id": <report_id>,
                    "plan": <plan_id>,
                    "uploaded_file": <file_url>,
                    ...
                },
                ...
            ]
            404: {"error": "Plan not found" / "audit report not found"}
        """
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
        """
        Delete a specific audit report by ID.

        This method authenticates the admin using the Authorization header and deletes a specific audit report
        identified by its ID.

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - If the audit report with the specified ID does not exist, an error is returned.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - trace_code (str, path): Unique identifier (ID) for the audit report to be deleted.

        Responses:
            200: {"message": "success"}
            400: {"error": "Authorization header is missing"}
            404: {"error": "admin not found" / "audit report not found"}
        """
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


class ParticipationReportViewset(APIView):
    """
    This view allows a user to retrieve their participation report for a specific crowdfunding project, identified by the plan's trace code.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get(self, request, trace_code):
        """
        Retrieve a participation report for a specific plan.

        This method authenticates the user using the Authorization header and retrieves a participation report for a
        specific plan identified by its trace code. The report is generated as a PDF file and stored on the server,
        with a URL link returned in the response.

        - If the Authorization header is missing, an error is returned.
        - If the user's authorization token is invalid or the user is not found, an error is returned.
        - If the plan with the specified trace code does not exist, an error is returned.
        - If an error occurs during report generation, an error is returned with the corresponding status.

        Parameters:
            - Authorization (str, header): User's authorization token.
            - trace_code (str, path): Unique trace code identifier for the plan.

        Responses:
            200: {
                "url": "/media/reports/<trace_code>_<national_id>.pdf"
            }
            400: {"error": "Authorization header is missing"}
            404: {"error": "user not found" / "plan not found"}
            Other (pass-through): Error responses from CrowdfundingAPI service
        """
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


class DashBoardAdminViewset (APIView) : 
    """
    This view provides an admin with an overview dashboard that includes statistics on plans and carts.
    """
    @method_decorator(ratelimit(key='ip', rate='20/m', method='GET', block=True))
    def get (self , request) :
        """
        Retrieve dashboard statistics for plans and carts.

        This method authenticates the admin using the Authorization header and returns a summary of
        statistics related to plans and carts, including counts of all plans, expired plans, active plans, 
        plans currently shown, all carts, expired carts, and active carts.

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.

        Parameters:
            - Authorization (str, header): Admin's authorization token.

        Responses:
            200: {
                "all plan": <total_plan_count>,
                "expire plan": <expired_plan_count>,
                "active plan": <active_plan_count>,
                "show_plan": <show_plan_count>,
                "all cart": <total_cart_count>,
                "expire cart": <expired_cart_count>,
                "active cart": <active_cart_count>
            }
            400: {"error": "Authorization header is missing"}
            401: {"error": "admin not found"}
        """
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
   

class DashBoardUserViewset(APIView):
    """
    This view provides an overview dashboard for users, including statistics on plans, payments, total investment, 
    rate of return, and profit dates.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get(self, request):
        """
        Retrieve user-specific dashboard statistics.

        This method authenticates the user using the Authorization header and returns a summary of statistics
        specific to the user, including:
        
        - Total number of plans
        - Number of active plans
        - User's participation in plans
        - Total value of user’s investments
        - Total rate of return
        - A list of profit dates, amounts, and types associated with the user’s participations

        Parameters:
            - Authorization (str, header): User's authorization token.

        Responses:
            200: {
                "all plan": <total_plan_count>,
                "active plan": <active_plan_count>,
                "participant plan": <user_participation_count>,
                "total value": <total_investment_value>,
                "all rate of return": <total_rate_of_return>,
                "profit": [
                    {
                        "type": <operation_type>,
                        "date": <jalali_date>,
                        "amount": <profit_amount>,
                        "plan": <plan_id>
                    },
                    ...
                ]
            }
            400: {"error": "Authorization header is missing"}
            404: {"error": "user not found"}
        """
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
    

class ProfitabilityReportViewSet(APIView):
    """
    This view provides a profitability report for a specific plan, identified by its trace code.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get(self, request, trace_code):
        """
        Retrieve profitability report for a specific plan by trace code.

        This method authenticates the admin using the Authorization header and generates a detailed profitability
        report for a specific plan, including user payments, calculated profits, and payment dates. The report 
        is based on the plan's rate of return and the project's end dates.

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - If the trace code, plan, or related information is missing, an error is returned.
        - If the plan has not ended, an error is returned.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - trace_code (str, path): Unique trace code identifier for the plan.

        Responses:
            200: [
                {
                    "user": <user_identifier>,
                    "amount": <user_investment_amount>,
                    "value": <user_investment_value>,
                    "account_number": <user_account_number>,
                    "user_name": <user_name>,
                    "profit1": <profit1_value>,
                    "value1": <value1_value>,
                    "date_operator1": <date1>,
                    ...
                },
                ...
            ]
            400: {"error": "Authorization header is missing" / "trace_code not found"}
            404: {"error": "admin not found" / "plan not found"}
            406: {"error": "plan not end" / "payment not found" / "information not found"}
        """
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
    