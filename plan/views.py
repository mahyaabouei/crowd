from .models import Plan , DocumentationFiles ,Appendices ,Comment  , Plans ,ListOfProjectBoardMembers,ProjectOwnerCompan , PaymentGateway ,PicturePlan ,Warranty, InformationPlan , EndOfFundraising ,ListOfProjectBigShareHolders,Complaint
from rest_framework.response import Response
from rest_framework import status 
from rest_framework.views import APIView
from authentication import fun
from . import serializers
from investor.models import Cart
from authentication.models import privatePerson , User , accounts , LegalPerson , tradingCodes ,Admin
import datetime
from persiantools.jdatetime import JalaliDate
from dateutil.relativedelta import relativedelta
import pandas as pd
from .CrowdfundingAPIService import CrowdfundingAPI , ProjectFinancingProvider
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import os
from django.conf import settings
from plan.PeymentPEP import PasargadPaymentGateway 
from django.db import transaction
from django.db.models import Q
from django_ratelimit.decorators import ratelimit   
from django.utils.decorators import method_decorator
from django.db.models import Sum
from utils.user_notifier import UserNotifier
from reports.models import AuditReport , ProgressReport

def get_name (uniqueIdentifier) :
    user = User.objects.filter(uniqueIdentifier=uniqueIdentifier).first()
    
    privateperson = privatePerson.objects.filter(user=user).first()
    if privateperson :
        first_name = privateperson.firstName
        last_name = privateperson.lastName
        full_name = first_name + ' ' + last_name
    elif LegalPerson.objects.filter(user=user).first() :
        legalperson = LegalPerson.objects.filter(user=user).first()
        full_name = legalperson.companyName
    else :
        full_name = 'N/A'
    return full_name

def get_name_user (uniqueIdentifier) :
    user = User.objects.filter(uniqueIdentifier=uniqueIdentifier).first()

    full_name = 'نامشخص'
    return full_name


def get_fname (uniqueIdentifier) :
    user = User.objects.filter(uniqueIdentifier=uniqueIdentifier).first()
    try:
        privateperson = privatePerson.objects.filter(user=user).first()
        first_name = privateperson.firstName
    except:
        return ""
    return first_name


def get_lname (uniqueIdentifier) :
    user = User.objects.filter(uniqueIdentifier=uniqueIdentifier).first()
    privateperson = privatePerson.objects.filter(user=user).first()
    if privateperson :
        last_name = privateperson.lastName
    elif LegalPerson.objects.filter(user=user).first() :
        legalperson = LegalPerson.objects.filter(user=user).first()
        last_name = legalperson.companyName
    return last_name

def get_economi_code (uniqueIdentifier) :
    user = User.objects.filter(uniqueIdentifier=uniqueIdentifier).first()
    economi_code = tradingCodes.objects.filter(user=user).first()
    if economi_code:
        economi_code = economi_code.code.strip()
    else:
        economi_code = ''
    return economi_code


def get_account_number(uniqueIdentifier) :
    user = User.objects.filter(uniqueIdentifier=uniqueIdentifier).first()
    user_account = accounts.objects.filter(user=user).first()
    sheba = user_account.sheba if user_account else ''
    return sheba 


def get_mobile_number(uniqueIdentifier) :
    user = User.objects.filter(uniqueIdentifier=uniqueIdentifier).first()
    mobile = user.mobile
    if mobile[:2] == '98':
      mobile = '0'+ mobile[2:]
    return mobile


def check_legal_person(uniqueIdentifier) :
    user = User.objects.filter(uniqueIdentifier=uniqueIdentifier).first()
    legal_person = LegalPerson.objects.filter(user=user).first()
    if legal_person:
        return True
    return False


def number_of_finance_provider(trace_code) :
    plan = Plan.objects.filter(trace_code=trace_code).first()
    if not plan :
        plan = 0
    payment = PaymentGateway.objects.filter(plan=plan).filter(Q(status='2') | Q(status='3')).values('user').distinct().count()   

    if not payment :
        payment = 0
    return payment 

def get_full_name_admin(uniqueIdentifier) :
    admin = Admin.objects.filter(uniqueIdentifier=uniqueIdentifier).first()
    if admin :
        return admin.firstName + ' ' + admin.lastName
    return 'N/A'


# done
# detial + information
class PlanViewset(APIView):
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get(self, request, trace_code):
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:
            return Response({'message': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)
        plan.number_of_finance_provider =number_of_finance_provider(trace_code=trace_code)
        plan_serializer = serializers.PlanSerializer(plan)
        board_members_list = []
        board_members = ListOfProjectBoardMembers.objects.filter(plan=plan)
        if board_members.exists():
            board_members_serializer = serializers.ListOfProjectBoardMembersSerializer(board_members, many=True)
            for i in board_members_serializer.data :
                member_data = {
                'plan' : i['plan'],
                'first_name' : i['first_name'],
                'last_name' : i['last_name'],
                'organization_post_description' : i['organization_post_description'],
                'company_name' : i['company_name'],
                'company_national_id' : i['company_national_id'],
                'is_agent_from_company' : i['is_agent_from_company'],
                'organization_post_id' : i['organization_post_id'],
                }
                board_members_list.append(member_data)
        shareholder = ListOfProjectBigShareHolders.objects.filter(plan=plan)
        if shareholder.exists():
            shareholder_serializer = serializers.ListOfProjectBigShareHoldersSerializer(shareholder, many=True)
            shareholder_list = []
            for j in shareholder_serializer.data :
                shareholder_data = {
                    'share_percent' : j['share_percent'],
                    'first_name' : j['first_name'],
                    'last_name' : j['last_name'],
                    'shareholder_type' : j['shareholder_type'],
                    'plan' : j['plan'],
                    }
                
                shareholder_list.append(shareholder_data)
        picture_plan = PicturePlan.objects.filter(plan=plan).first()
        picture_plan = serializers.PicturePlanSerializer(picture_plan)
        company = ProjectOwnerCompan.objects.filter(plan=plan)
        if company.exists():
            company_serializer = serializers.ProjectOwnerCompansSerializer(company, many=True)

        response_data = {
            'plan': plan_serializer.data ,
            'board_member' :board_members_list , 
            'shareholder' : shareholder_list,
            'company': company_serializer.data,
            'picture_plan': picture_plan.data,
        }
        information = InformationPlan.objects.filter(plan=plan).first()
        if information:
            information_serializer = serializers.InformationPlanSerializer(information)
            date_start = information.payment_date
            if isinstance(date_start, str):
                date_start = datetime.datetime.strptime(date_start, '%Y-%m-%dT%H:%M:%S')     
            response_data['information_complete'] = information_serializer.data
            response_data['date_start'] = date_start

        end_of_fundraising = EndOfFundraising.objects.filter(plan=plan)
        if end_of_fundraising :
            try:
                end_of_fundraising_serializer = serializers.EndOfFundraisingSerializer(end_of_fundraising , many = True)
                date_profit = []
                for i in end_of_fundraising_serializer.data :
                    date = i['date_operator']
                    type = i['type']
                    date = datetime.datetime.strptime(date , '%Y-%m-%d')
                    date_jalali = JalaliDate.to_jalali(date)
                    date_jalali =str(date_jalali)
                    date_profit.append({'type': type, 'date': date_jalali})
                response_data['date_profit'] = date_profit
            except :
                response_data['date_profit'] = []

        return Response(response_data, status=status.HTTP_200_OK)
        

# done
# list + information
# update
class PlansViewset(APIView):
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get(self, request):
        plans = Plan.objects.all()
        result = []

        for plan in plans:
            trace_code = plan.trace_code
            plan_number_of_finance_provider = number_of_finance_provider(trace_code=trace_code)
            plan.number_of_finance_provider = plan_number_of_finance_provider
            plan.save()
            information = InformationPlan.objects.filter(plan=plan).first()
            if information and information.status_second == '1':
                payment_all = PaymentGateway.objects.filter(plan=plan)
                if payment_all.exists():
                    payment_all = serializers.PaymentGatewaySerializer(payment_all, many=True)
                    payment_df = pd.DataFrame(payment_all.data)
                    payment_df = payment_df[['status', 'value']]
                    payment_df = payment_df[payment_df['status'].isin(['2', '3'])]
                    collected = payment_df['value'].sum()
                    information.amount_collected_now = collected
                    information.save()
            information = InformationPlan.objects.filter(plan=plan).first()
            board_members = ListOfProjectBoardMembers.objects.filter(plan=plan)  
            company = ProjectOwnerCompan.objects.filter(plan=plan)  
            shareholder = ListOfProjectBigShareHolders.objects.filter(plan=plan)  
            plan_serializer = serializers.PlanSerializer(plan)
            board_members_serializer = serializers.ListOfProjectBoardMembersSerializer(board_members, many=True)
            board_members_list = []
            for i in board_members_serializer.data :
                member_data = {
                'plan' : i['plan'],
                'first_name' : i['first_name'],
                'last_name' : i['last_name'],
                'organization_post_description' : i['organization_post_description'],
                'company_name' : i['company_name'],
                'company_national_id' : i['company_national_id'],
                'is_agent_from_company' : i['is_agent_from_company'],
                'organization_post_id' : i['organization_post_id'],
                }
                board_members_list.append(member_data)
            shareholder_serializer = serializers.ListOfProjectBigShareHoldersSerializer(shareholder, many=True)
            shareholder_list = []
            for j in shareholder_serializer.data :
                shareholder_data = {
                    'share_percent' : j['share_percent'],
                    'first_name' : j['first_name'],
                    'last_name' : j['last_name'],
                    'shareholder_type' : j['shareholder_type'],
                    'plan' : j['plan'],
                    }
                
                shareholder_list.append(shareholder_data)
            company_serializer = serializers.ProjectOwnerCompansSerializer(company, many=True)
            picture_plan = PicturePlan.objects.filter(plan=plan).first()
            picture_plan = serializers.PicturePlanSerializer(picture_plan)
        
            data = {
                'plan': plan_serializer.data,
                'board_members': board_members_list , 
                'shareholder': shareholder_list  ,
                'company': company_serializer.data  ,
                'picture_plan': picture_plan.data
            }
            if information:
                information_serializer =serializers.InformationPlanSerializer(information)
                data['information_complete'] = information_serializer.data
            result.append(data)

        return Response(result, status=status.HTTP_200_OK)
    
    @method_decorator(ratelimit(key='ip', rate='50/m', method='PATCH', block=True))
    def patch(self, request):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        crowd_founding_api = CrowdfundingAPI()
        plan_list = crowd_founding_api.get_company_projects()
        
        BASE_URL = os.getenv('BASE_URL')
        API_KEY = os.getenv('API_KEY')


        for i in plan_list : 
            if not Plans.objects.filter(plan_id = i).exists () :
                plan = Plans.objects.create(plan_id=i)
        for i in plan_list:    
            plan_detail = crowd_founding_api.get_project_info(i)

        
            plan, created = Plan.objects.update_or_create(
                trace_code=i,
                defaults={
                    'creation_date': plan_detail.get('Creation Date', None),
                    'persian_name': plan_detail.get('Persian Name', None),
                    'persian_suggested_symbol': plan_detail.get('Persian Suggested Symbol', None),
                    'persoan_approved_symbol': plan_detail.get('Persoan Approved Symbol', None),
                    'english_name': plan_detail.get('English Name', None),
                    'english_suggested_symbol': plan_detail.get('English Suggested Symbol', None),
                    'english_approved_symbol': plan_detail.get('English Approved Symbol', None),
                    'industry_group_id': plan_detail.get('Industry Group ID', None),
                    'industry_group_description': plan_detail.get('Industry Group Description', None),
                    'sub_industry_group_id': plan_detail.get('Sub Industry Group ID', None),
                    'sub_industry_group_description': plan_detail.get('Sub Industry Group Description', None),
                    'persian_subject': plan_detail.get('Persian Subject', None),
                    'english_subject': plan_detail.get('English Subject', None),
                    'unit_price': plan_detail.get('Unit Price', None),
                    'total_units': plan_detail.get('Total Units', None),
                    'company_unit_counts': plan_detail.get('Company Unit Counts', None),
                    'total_price': plan_detail.get('Total Price', None),
                    'crowd_funding_type_id': plan_detail.get('Crowd Funding Type ID', None),
                    'crowd_funding_type_description': plan_detail.get('Crowd Funding Type Description', None),
                    'float_crowd_funding_type_description': plan_detail.get('Float Crowd Funding Type Description', None),
                    'minimum_required_price': plan_detail.get('Minimum Required Price', None),
                    'real_person_minimum_availabe_price': plan_detail.get('Real Person Minimum Availabe Price', None),
                    'real_person_maximum_available_price': plan_detail.get('Real Person Maximum Available Price', None),
                    'legal_person_minimum_availabe_price': plan_detail.get('Legal Person Minimum Availabe Price', None),
                    'legal_person_maximum_availabe_price': plan_detail.get('Legal Person Maximum Available Price', None),
                    'underwriting_duration': plan_detail.get('Underwriting Duration', None),
                    'suggested_underwriting_start_date': plan_detail.get('Suggested Underwriting Start Date', None),
                    'suggested_underwriting_end_date': plan_detail.get('Suggested Underwriting End Date', None),
                    'approved_underwriting_start_date': plan_detail.get('Approved Underwriting Start Date', None),
                    'approved_underwriting_end_date': plan_detail.get('Approved Underwriting End Date', None),
                    'project_start_date': plan_detail.get('Project Start Date', None),
                    'project_end_date': plan_detail.get('Project End Date', None),
                    'settlement_description': plan_detail.get('Settlement Description', None),
                    'project_status_description': plan_detail.get('Project Status Description', None),
                    'project_status_id': plan_detail.get('Project Status ID', None),
                    'persian_suggested_underwiring_start_date': plan_detail.get('Persian Suggested Underwiring Start Date', None),
                    'persian_suggested_underwriting_end_date': plan_detail.get('Persian Suggested Underwriting End Date', None),
                    'persian_approved_underwriting_start_date': plan_detail.get('Persian Approved Underwriting Start Date', None),
                    'persian_approved_underwriting_end_date': plan_detail.get('Persian Approved Underwriting End Date', None),
                    'persian_project_start_date': plan_detail.get('Persian Project Start Date', None),
                    'persian_project_end_date': plan_detail.get('Persian Project End Date', None),
                    'persian_creation_date': plan_detail.get('Persian Creation Date', None),
                    # 'number_of_finance_provider': plan_detail.get('Number of Finance Provider', None),
                    'sum_of_funding_provided': plan_detail.get('SumOfFundingProvided', None)
                }
            )
            trace_code = plan.trace_code
            plan.number_of_finance_provider = number_of_finance_provider(trace_code)
            plan.save()

            if len(plan_detail.get('Project Owner Company', [])) > 0:
                for j in plan_detail['Project Owner Company']:
                    project_owner_company, _ = ProjectOwnerCompan.objects.update_or_create(
                        plan=plan,
                        national_id=j.get('National ID', None),
                        defaults={
                            'name': j.get('Name', None),
                            'compnay_type_id': j.get('Company Type ID', None),
                            'company_type_description': j.get('Company Type Description', None),
                            'registration_date': j.get('Registration Date', None),
                            'registration_number': j.get('Registration Number', None),
                            'economic_id': j.get('Economic ID', None),
                            'address': j.get('Address', None),
                            'postal_code': j.get('Postal Code', None),
                            'phone_number': j.get('Phone Number', None),
                            'fax_number': j.get('Fax Number', None),
                            'email_address': j.get('Email Address', None)
                        }
                    )

            if len(plan_detail.get('List Of Project Big Share Holders', [])) > 0:
                for j in plan_detail['List Of Project Big Share Holders']:
                    List_of_project_big_shareholder, _ = ListOfProjectBigShareHolders.objects.update_or_create(
                        plan=plan,
                        national_id=j.get('National ID', None),
                        defaults={
                            'shareholder_type': j.get('Shareholder Type', None),
                            'first_name': j.get('First Name / Company Name', None),
                            'last_name': j.get('Last Name / CEO Name', None),
                            'share_percent': j.get('Share Percent', None),
                            
                        }
                    )



            if len(plan_detail.get('List Of Project Board Members', [])) > 0:
                for j in plan_detail['List Of Project Board Members']:
                    List_of_project_board_members, _ = ListOfProjectBoardMembers.objects.update_or_create(
                        plan=plan,
                        national_id=j.get('National ID', None),
                        defaults={
                            'mobile_number': j.get('mobile_number', None),
                            'email_address': j.get('email_address', None),
                            'organization_post_id': j.get('Organization Post ID', None),
                            'is_agent_from_company': j.get('Is Agent from a Company', None),
                            'first_name': j.get('First Name', None),
                            'last_name': j.get('Last Name', None),
                            'company_national_id': j.get('Company National ID', None),
                            'company_name': j.get('Company Name', None),
                            'mobile_number': j.get('Mobile Number', None),
                            'email_address': j.get('Email Address', None),
                            'organization_post_description': j.get('Organization Post Description', None),
                            
                        }
                    )


        return Response({'message':'بروزرسانی از فرابورس انجام شد'}, status=status.HTTP_200_OK)
# done

class AppendicesViewset(APIView) :
    @method_decorator(ratelimit(key='ip', rate='50/m', method='POST', block=True))
    def post (self,request,trace_code) :
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
        data = request.data.copy()
        serializer = serializers.AppendicesSerializer(data=data)
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
        appendices = Appendices.objects.filter(plan=plan)
        if not appendices.exists() :
            return Response({'error': 'Appendices not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.AppendicesSerializer(appendices, many= True)
        return Response(serializer.data , status=status.HTTP_200_OK)
    @method_decorator(ratelimit(key='ip', rate='50/m', method='DELETE', block=True))
    def delete(self,request,trace_code):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        appendices = Appendices.objects.filter(id=int(trace_code))
        if not appendices.exists() :
            return Response({'error': 'Appendices not found'}, status=status.HTTP_404_NOT_FOUND)
        appendices.delete()
        return Response({'message':'succes'} , status=status.HTTP_200_OK)
    
# done
class DocumentationViewset(APIView) :
    @method_decorator(ratelimit(key='ip', rate='50/m', method='POST', block=True))
    def post (self,request,trace_code) :
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
        data = request.data.copy()
        serializer = serializers.DocumentationSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if 'file' in request.FILES:
            serializer.uploaded_file = request.FILES['file']



        serializer.save(plan=plan)
        return Response ({'data' : serializer.data} , status=status.HTTP_200_OK)
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get (self,request,trace_code) :

        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:
            return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)
        ducumentation = DocumentationFiles.objects.filter(plan=plan)
        serializer = serializers.DocumentationSerializer(ducumentation, many= True)
        return Response(serializer.data , status=status.HTTP_200_OK)
    @method_decorator(ratelimit(key='ip', rate='50/m', method='DELETE', block=True))
    def delete(self,request,trace_code):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        appendices = DocumentationFiles.objects.filter(id=int(trace_code))
        if not appendices.exists() :
            return Response({'error': 'Appendices not found'}, status=status.HTTP_404_NOT_FOUND)
        appendices.delete()
        return Response({'message':'succses'} , status=status.HTTP_200_OK)
# done
class CommentAdminViewset (APIView) :
    @method_decorator(ratelimit(key='ip', rate='50/m', method='GET', block=True))
    def get (self,request,trace_code) :
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

        comments = Comment.objects.filter(plan=plan)
        for comment in comments:
            if comment.answer is None or comment.answer == '':
                comment.answer = 'منتظر پاسخ'
                comment.save()  

        serializer = serializers.CommenttSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    @method_decorator(ratelimit(key='ip', rate='50/m', method='PATCH', block=True))
    def patch (self,request,trace_code) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()     
        comment = Comment.objects.filter(id=trace_code).first()
        if not comment:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data
        data['answer'] = data.get('answer', 'منتظر پاسخ') or 'منتظر پاسخ'
        serializer = serializers.CommenttSerializer(comment, data=data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

# done
class CommentViewset (APIView):
    @method_decorator(ratelimit(**settings.RATE_LIMIT['POST']), name='post')
    def post (self,request,trace_code):
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
        data = request.data.copy()
        if not data['known']:
            data['known'] = False
        if not data['comment']:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
        comment = Comment(plan=plan , user=user, known=data['known'] ,comment= data['comment'] ,answer='منتظر پاسخ')
        comment.save()
        return Response(True,status=status.HTTP_200_OK)
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get (self,request,trace_code) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_401_UNAUTHORIZED)
        user = user.first()
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:
            return Response({'error': 'Plan not found'}, status=status.HTTP_400_BAD_REQUEST)

        private_person = privatePerson.objects.filter(user=user).first()
        if not private_person:
            return Response({'error': 'privatePerson not found'}, status=status.HTTP_404_NOT_FOUND)

        comments = Comment.objects.filter(plan=plan, status=True)
        if not comments.exists():
            return Response({'error': 'comments not found or no status true'}, status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.CommenttSerializer(comments, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

#done
class SendpicturePlanViewset(APIView) :
    @method_decorator(ratelimit(key='ip', rate='50/m', method='POST', block=True))
    def post (self,request,trace_code) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:
            return Response({'error': 'plan not found'}, status=status.HTTP_404_NOT_FOUND)
        if 'picture' not in request.FILES:
            return Response({'error': 'No picture file was uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        picture = PicturePlan.objects.filter(plan=plan).first()
        if picture :
            picture.delete()
        picture = PicturePlan.objects.create(plan=plan , picture = request.FILES['picture'])
        picture.save()
        return Response({'success': True, 'message': 'Picture updated successfully'}, status=status.HTTP_200_OK)


    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get (self,request,trace_code) :
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:
            return Response({'error': 'plan not found'}, status=status.HTTP_404_NOT_FOUND)
        picture = PicturePlan.objects.filter(plan=plan).first()
        serializer = serializers.PicturePlanSerializer(picture)
        return Response(serializer.data, status=status.HTTP_200_OK)


# done
# محدودیت پرداخت به دلیل امنیت غیر فعال شد
class PaymentDocument(APIView):
    @method_decorator(ratelimit(**settings.RATE_LIMIT['POST']), name='post')
    def post(self,request,trace_code):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_401_UNAUTHORIZED)
        user = user.first()

        legal_user = check_legal_person(user.uniqueIdentifier)

        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:
            return Response({'error': 'plan not found'}, status=status.HTTP_404_NOT_FOUND)
        
        information_plan = InformationPlan.objects.filter(plan=plan).first()

        if not request.data.get('amount'):
            return Response({'error': 'amount not found'}, status=status.HTTP_404_NOT_FOUND)
        
        amount = int(request.data.get('amount')) # سهم درخواستی کاربر 
        amount_collected_now = information_plan.amount_collected_now # مبلغ جمه اوری شده تا به  الان
        plan_unit_price = plan.unit_price 
        value = plan_unit_price * amount
        plan_total_price = plan.total_price # کل قیمت قابل عرضه برای طرح 

        if not request.data.get('payment_id'):
            return Response({'error': 'payment_id not found'}, status=status.HTTP_404_NOT_FOUND)
        payment_id = request.data.get('payment_id')
        existing_payment = PaymentGateway.objects.filter(plan=plan,payment_id=payment_id,status__in=['2','3']).first()
        if existing_payment:
            return Response({'error': 'payment_id already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        purchaseable_value = int((plan_total_price or 0) - (amount_collected_now or 0))
        if value > purchaseable_value :
            return Response({'error': 'مبلغ بیشتر از سهم قابل خرید است'}, status=status.HTTP_400_BAD_REQUEST)
        
        if legal_user == True : 
            amount_legal_min = plan.legal_person_minimum_availabe_price #حداقل سهم قابل خرید حقوقی 
            amount_legal_max = plan.legal_person_maximum_availabe_price #حداکثر سهم قابل خرید حقوقی
            
            if not amount_legal_min :
                amount_legal_min = plan_unit_price
            if not amount_legal_max :
                amount_legal_max = purchaseable_value

            if value < amount_legal_min :
                return Response({'error': 'مبلغ  کمتر از  حد مجاز قرارداد شده است'}, status=status.HTTP_400_BAD_REQUEST)
            if value > amount_legal_max:
                print(value,amount_legal_max)
                return Response({'error': 'مبلغ بیشتر  از  حد مجاز قرارداد شده است'}, status=status.HTTP_400_BAD_REQUEST)
            if value > purchaseable_value :
                return Response({'error': 'مبلغ بیشتر از سهم قابل خرید است'}, status=status.HTTP_400_BAD_REQUEST)
                
                
        else :
            amount_personal_min = int(plan.real_person_minimum_availabe_price)  #حداقل سهم قابل خرید حقیقی
            amount_personal_max = int(plan.real_person_maximum_available_price) #حداکثر سهم قابل خرید حقیقی
            if not amount_personal_min :
                amount_personal_min = plan_unit_price
            if not amount_personal_max :
                amount_personal_max = purchaseable_value

            if value < amount_personal_min :
                return Response({'error': 'مبلغ  کمتر از  حد مجاز قرارداد شده است'}, status=status.HTTP_400_BAD_REQUEST)
            if value > amount_personal_max :
                return Response({'error': 'مبلغ بیشتر  از  حد مجاز قرارداد شده است'}, status=status.HTTP_400_BAD_REQUEST)
            
            if value > purchaseable_value :
                return Response({'error': 'مبلغ بیشتر از سهم قابل خرید است'}, status=status.HTTP_400_BAD_REQUEST)
                


        description = request.data.get('description',None)
        if not request.data.get('risk_statement'):
            return Response({'error': 'risk_statement not found'}, status=status.HTTP_404_NOT_FOUND)
            
        risk_statement = request.data.get('risk_statement') == 'true'
        if not risk_statement:
            return Response({'error': 'risk_statement not true'}, status=status.HTTP_404_NOT_FOUND)
        if not request.data.get('name_status'):
            return Response({'error': 'name_status not found'}, status=status.HTTP_404_NOT_FOUND)
        name_status = request.data.get('name_status') == 'true'
        if not request.FILES.get('picture'):
            return Response({'error': 'picture not found'}, status=status.HTTP_404_NOT_FOUND)
        picture = request.FILES.get('picture')
        payment = PaymentGateway(
            plan = plan,
            user = user.uniqueIdentifier,
            amount = amount,
            value = value,
            payment_id = payment_id,
            track_id = payment_id,
            description = description,
            name_status = name_status,
            picture = picture,
            
        )
        payment.save()
        return Response('success')
    
    @method_decorator(ratelimit(key='ip', rate='50/m', method='GET', block=True))
    def get(self,request,trace_code):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)

        admin = fun.decryptionadmin(Authorization)


        if not admin :
            return Response({'error': 'Authorization not found'}, status=status.HTTP_401_UNAUTHORIZED)
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:
            return Response({'error': 'plan not found'}, status=status.HTTP_404_NOT_FOUND)

        admin = admin.first()
        payments = PaymentGateway.objects.filter(plan=plan)
        response = serializers.PaymentGatewaySerializer(payments,many=True)

        df = pd.DataFrame(response.data)
        if len(df)==0:
            return Response([], status=status.HTTP_200_OK)
        df['fulname'] = [get_name(x) for x in df['user']]
        
        df = df.fillna('')
        df = df.to_dict('records')

        return Response(df, status=status.HTTP_200_OK)
    
        

            
    @method_decorator(ratelimit(key='ip', rate='50/m', method='PATCH', block=True))
    def patch (self,request,trace_code) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:
            return Response({'error': 'plan not found'}, status=status.HTTP_404_NOT_FOUND)
        payment_id = request.data.get('id')
        payments = PaymentGateway.objects.filter(plan=plan,id = payment_id).first()
        if not payments :
            return Response({'error': 'payments not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.PaymentGatewaySerializer(payments, data = request.data , partial = True)
        if serializer.is_valid () :
            serializer.save()
        payment_all = PaymentGateway.objects.filter(plan=plan)
        value = 0
        for i in payment_all : 
            if i.status == '2' or i.status == '3':
               value += i.value
        information = InformationPlan.objects.filter(plan=plan).first()
        information.amount_collected_now = value
        information.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class PaymentUserReport(APIView):
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get(self,request,trace_code):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'Authorization not found'}, status=status.HTTP_401_UNAUTHORIZED)
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:
            return Response({'error': 'plan not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()
        payments = PaymentGateway.objects.filter(plan=plan , status__in=['2', '3'])
        response = serializers.PaymentGatewaySerializer(payments,many=True)
        df = pd.DataFrame(response.data)
        if len(df)==0:
            return Response([], status=status.HTTP_200_OK)
        df['fullname'] = df.apply(lambda row: get_name(row['user']) if row['name_status'] else 'نامشخص', axis=1)
        df = df[['amount','value','create_date','fullname']]
        df = df.to_dict('records')
        return Response(df, status=status.HTTP_200_OK)


class PaymentUser(APIView):
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get(self,request,trace_code):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'Authorization not found'}, status=status.HTTP_401_UNAUTHORIZED)
        user = user.first()
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:

            return Response({'error': 'plan not found'}, status=status.HTTP_404_NOT_FOUND)
        payments = PaymentGateway.objects.filter(plan=plan,user=user.uniqueIdentifier)
        response = serializers.PaymentGatewaySerializer(payments,many=True)
        return Response(response.data, status=status.HTTP_200_OK)

# done
class ParticipantViewset(APIView) :
    @method_decorator(ratelimit(key='ip', rate='50/m', method='GET', block=True))
    def get(self, request,trace_code):
        Authorization = request.headers.get('Authorization')
        if  Authorization:
            admin = fun.decryptionadmin(Authorization)
            if not admin:
                return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
            admin = admin.first()
        else :
            admin= False
        plan = Plan.objects.filter(trace_code = trace_code).first()
        if not plan :
            return Response ({'error': 'plan not found'}, status=status.HTTP_404_NOT_FOUND)
        participant = PaymentGateway.objects.filter(plan=plan , status= '3')
        if not participant :
            return Response ({'error': 'participant not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.PaymentGatewaySerializer(participant , many= True)
        names = []

        df = pd.DataFrame(serializer.data)
        df = df.drop(['picture', 'risk_statement', 'cart_number', 'code', 'description'] , axis=1)
        for index, row in df.iterrows():
            
            if row['name_status'] == True or admin:
                name = get_name(row['user'])
            else : 
                name = 'نامشخص'
            names.append(name)
        df['name'] = names
        df= df.sort_values(by='user')
        df = df.to_dict('records')
              
        return Response (df, status=status.HTTP_200_OK)


class Certificate(APIView):
    @method_decorator(ratelimit(**settings.RATE_LIMIT['POST']), name='post')
    def post(self,request,trace_code):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'Authorization not found'}, status=status.HTTP_401_UNAUTHORIZED)
        user = user.first()
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:
            return Response({'error': 'plan not found'}, status=status.HTTP_404_NOT_FOUND)
        apiFarabours = CrowdfundingAPI()
        participation = apiFarabours.get_project_participation_report(trace_code , user.uniqueIdentifier)
        if participation.status_code != 200:
            return Response(participation.json(),status=status.HTTP_200_OK)
        file_name = f"{trace_code}_{user.uniqueIdentifier}.pdf"
        file_path = os.path.join(settings.MEDIA_ROOT, 'reports', file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as pdf_file:
            pdf_file.write(participation.content)
        return Response({'url':f'/media/reports/{file_name}'},status=status.HTTP_200_OK)
    
# گواهی مشارکت ادمین
class CertificateAdminViewset(APIView):
    @method_decorator(ratelimit(key='ip', rate='50/m', method='GET', block=True))
    def post (self,request , trace_code):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        data = request.data.get('uniqueIdentifier')
        if not data:
            return Response({'error': 'uniqueIdentifier is required'}, status=status.HTTP_400_BAD_REQUEST)  
        user = User.objects.filter(uniqueIdentifier=data).first()
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)  
        apiFarabours = CrowdfundingAPI()
        participation = apiFarabours.get_project_participation_report(trace_code , user.uniqueIdentifier)
        if participation.status_code != 200:
            return Response(participation.json(),status=status.HTTP_200_OK)
        file_name = f"{trace_code}_{user.uniqueIdentifier}.pdf"
        file_path = os.path.join(settings.MEDIA_ROOT, 'reports', file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as pdf_file:
            pdf_file.write(participation.content)
        return Response({'url':f'/media/reports/{file_name}'},status=status.HTTP_200_OK)
        

class InformationPlanViewset(APIView) :
    @method_decorator(ratelimit(**settings.RATE_LIMIT['POST']), name='post')
    def post (self,request,trace_code):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first() 
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan :
            return Response({'error': 'Invalid plan status'}, status=status.HTTP_400_BAD_REQUEST)
        rate_of_return = request.data.get('rate_of_return')
        status_second = request.data.get('status_second')
        status_show = request.data.get('status_show')
        payment_date = request.data.get('payment_date')
        if status_second not in ['1' , '2','3' , '4' , '5'] :
            status_second = '1'
        if payment_date :
            payment_date = int(payment_date)/1000
            payment_date = datetime.datetime.fromtimestamp(payment_date)
        information , _ = InformationPlan.objects.update_or_create(plan=plan ,defaults={'rate_of_return' : rate_of_return , 'status_second': status_second, 'status_show' :status_show , 'payment_date' :payment_date } )
        serializer = serializers.InformationPlanSerializer(information)
        

        return Response(serializer.data, status=status.HTTP_200_OK)
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get(self,request,trace_code) : 
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan :
            return Response({'error': 'Invalid plan status'}, status=status.HTTP_400_BAD_REQUEST)
        information = InformationPlan.objects.filter(plan=plan).first()
        serializer = serializers.InformationPlanSerializer(information)
        return Response(serializer.data, status=status.HTTP_200_OK)


#done
class EndOfFundraisingViewset(APIView) :
    @method_decorator(ratelimit(**settings.RATE_LIMIT['POST']), name='post')
    def post (self,request,trace_code):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan :
            return Response({'error': 'Invalid plan status'}, status=status.HTTP_400_BAD_REQUEST)
        information = InformationPlan.objects.filter(plan=plan).first()
        if not information:
            return Response({'error': 'information plan not found'}, status=status.HTTP_404_NOT_FOUND)
        date_payement = information.payment_date
        if isinstance(date_payement, str):
            date_payement = datetime.datetime.strptime(date_payement, '%Y-%m-%dT%H:%M:%S')
           
        all_end_fundraising = []
        end_fundraising = EndOfFundraising.objects.filter(plan=plan)
        if not end_fundraising :
            return Response({'error': 'end of fundraising not found'}, status=status.HTTP_404_NOT_FOUND)        
        # EndOfFundraising.objects.filter(plan=plan).delete()
        data = request.data 
        updated_items=[]
        for item in data:
            fundraising_id = item.get('id')
            if fundraising_id is None:
                return Response({'error': 'ID is required for each fundraising item'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                fundraising_instance = EndOfFundraising.objects.get(id=fundraising_id, plan=plan)
                fundraising_instance.amount_operator = item.get('amount_operator', fundraising_instance.amount_operator)
                fundraising_instance.date_operator = item.get('date_operator', fundraising_instance.date_operator)
                fundraising_instance.date_capitalization_operator = item.get(
                    'date_capitalization_operator', fundraising_instance.date_capitalization_operator
                )
                fundraising_instance.type = item.get('type', fundraising_instance.type)

                fundraising_instance.save()

                updated_items.append(fundraising_instance)

            except EndOfFundraising.DoesNotExist:
                return Response({'error': f'Fundraising with ID {fundraising_id} not found.'}, 
                                status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.EndOfFundraisingSerializer(updated_items, many=True, partial=True)

        return Response({'date_payement' : serializer.data , 'date_start' : date_payement}, status=status.HTTP_200_OK)


    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get(self,request,trace_code) : 
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first() 
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan :
            return Response({'error': 'Invalid plan status'}, status=status.HTTP_400_BAD_REQUEST)
        information = InformationPlan.objects.filter(plan=plan).first()
        if not information:
            return Response({'error': 'information plan not found'}, status=status.HTTP_404_NOT_FOUND)
        date_payement = information.payment_date
        if isinstance(date_payement, str):
            date_payement = datetime.datetime.strptime(date_payement, '%Y-%m-%dT%H:%M:%S')
            
        end_fundraising = EndOfFundraising.objects.filter(plan=plan)
        if end_fundraising.exists():
            serializer = serializers.EndOfFundraisingSerializer(end_fundraising , many = True).data

            return Response({'date_payments' : serializer ,'date_start' :  date_payement}, status=status.HTTP_200_OK)
        if not end_fundraising.exists():
            all_end_fundraising = []
            amount_fundraising = plan.sum_of_funding_provided
            if amount_fundraising:
                amount_fundraising = amount_fundraising / 4
            else:
                amount_fundraising = 0
            
            date = information.payment_date
            if date is None :
                return Response({'error': 'payment date not found'}, status=status.HTTP_404_NOT_FOUND)
            if isinstance(date, str):
                date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
            date = date + relativedelta(months=3) # از سه ماه اینده سود دهی شروع میشود

            for i in range(4):
                format_date = date.strftime('%Y-%m-%d') # تاریخ سود 
                date_capitalization = (date - timedelta(days=5)).date() #  تاریخ چک سود

                end_fundraising = EndOfFundraising.objects.create(
                    plan=plan,
                    date_systemic=format_date,
                    date_operator=format_date,
                    amount_systemic=amount_fundraising,
                    amount_operator=amount_fundraising,
                    type=2,
                    date_capitalization_systemic=date_capitalization,
                    date_capitalization_operator=date_capitalization
                )
                all_end_fundraising.append(end_fundraising)
                date = date + relativedelta(months=3)
                last_calculated_date = date - relativedelta(months=3) # تاریخ چک اصل پول 
                

class PaymentUser(APIView):
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get(self,request,trace_code):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'Authorization not found'}, status=status.HTTP_401_UNAUTHORIZED)
        user = user.first()
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:

            return Response({'error': 'plan not found'}, status=status.HTTP_404_NOT_FOUND)
        payments = PaymentGateway.objects.filter(plan=plan,user=user.uniqueIdentifier)
        response = serializers.PaymentGatewaySerializer(payments,many=True)
        return Response(response.data, status=status.HTTP_200_OK)

# done
class ParticipantViewset(APIView) :
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get(self, request,trace_code):
        Authorization = request.headers.get('Authorization')
        if  Authorization:
            admin = fun.decryptionadmin(Authorization)
            if not admin:
                return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
            admin = admin.first()
        else :
            admin= False
        plan = Plan.objects.filter(trace_code = trace_code).first()
        if not plan :
            return Response ({'error': 'plan not found'}, status=status.HTTP_404_NOT_FOUND)
        participant = PaymentGateway.objects.filter(plan=plan , status= '3')
        if not participant :
            return Response ({'error': 'participant not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.PaymentGatewaySerializer(participant , many= True)
        names = []

        df = pd.DataFrame(serializer.data)
        df = df.drop(['picture', 'risk_statement', 'cart_number', 'code', 'description'] , axis=1)
        for index, row in df.iterrows():
            
            if row['name_status'] == True or admin:
                name = get_name(row['user'])
            else : 
                name = 'نامشخص'
            names.append(name)
        df['name'] = names
        df= df.sort_values(by='user')
        df = df.to_dict('records')
              
        return Response (df, status=status.HTTP_200_OK)


class Certificate(APIView):
    @method_decorator(ratelimit(**settings.RATE_LIMIT['POST']), name='post')
    def post(self,request,trace_code):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'Authorization not found'}, status=status.HTTP_401_UNAUTHORIZED)
        user = user.first()
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:
            return Response({'error': 'plan not found'}, status=status.HTTP_404_NOT_FOUND)
        apiFarabours = CrowdfundingAPI()
        participation = apiFarabours.get_project_participation_report(trace_code , user.uniqueIdentifier)
        if participation.status_code != 200:
            return Response(participation.json(),status=status.HTTP_200_OK)
        file_name = f"{trace_code}_{user.uniqueIdentifier}.pdf"
        file_path = os.path.join(settings.MEDIA_ROOT, 'reports', file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as pdf_file:
            pdf_file.write(participation.content)
        return Response({'url':f'/media/reports/{file_name}'},status=status.HTTP_200_OK)
    
# گواهی مشارکت ادمین
class CertificateAdminViewset(APIView):
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def post (self,request , trace_code):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        if not isinstance(request.data, dict):
            return Response({'error': 'Invalid request data format'}, status=status.HTTP_400_BAD_REQUEST)
        unique_identifier = request.data.get('uniqueIdentifier')
        if not unique_identifier:
            return Response({'error': 'uniqueIdentifier is required'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(uniqueIdentifier=unique_identifier).first()
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)  
        apiFarabours = CrowdfundingAPI()
        participation = apiFarabours.get_project_participation_report(trace_code , user.uniqueIdentifier)
        if participation.status_code != 200:
            return Response(participation.json(),status=status.HTTP_200_OK)
        file_name = f"{trace_code}_{user.uniqueIdentifier}.pdf"
        file_path = os.path.join(settings.MEDIA_ROOT, 'reports', file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as pdf_file:
            pdf_file.write(participation.content)
        return Response({'url':f'/media/reports/{file_name}'},status=status.HTTP_200_OK)
            

class InformationPlanViewset(APIView) :
    @method_decorator(ratelimit(**settings.RATE_LIMIT['POST']), name='post')
    def post (self,request,trace_code):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first() 
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan :
            return Response({'error': 'Invalid plan status'}, status=status.HTTP_400_BAD_REQUEST)
        rate_of_return = request.data.get('rate_of_return')
        status_second = request.data.get('status_second')
        status_show = request.data.get('status_show')
        payment_date = request.data.get('payment_date')
        if payment_date == '':
            payment_date = None
        payback_period = request.data.get('payback_period')
        period_length = request.data.get('period_length')   
        

        if status_second not in ['1' , '2','3' , '4' , '5'] :
            status_second = '1'
        if payment_date :
            payment_date = int(payment_date)/1000
            payment_date = datetime.datetime.fromtimestamp(payment_date)
            for i in range(2):
                date = payment_date + relativedelta(months=i*6)
                title = f'گزارش حسابرسی 6 ماهه {(i + 1)}'
                audit_report = AuditReport.objects.filter(date=date, plan=plan).first()
                if audit_report:
                    audit_report.title = title
                    audit_report.period = i 
                    audit_report.date = date
                else:
                    audit_report = AuditReport.objects.create(date=date, title=title, period=i, plan=plan)
                
                audit_report.save()
            for i in range(4):
                title = f'گزارش پیشرفت {i+1}'
                progress_report = ProgressReport.objects.filter(date=date, plan=plan).first()   
                if progress_report:
                    progress_report.title = title
                    progress_report.period = i
                    progress_report.date = date
                else:
                    progress_report = ProgressReport.objects.create(date=date, title=title, period=i, plan=plan)
                progress_report.save()
        information , _ = InformationPlan.objects.update_or_create(plan=plan ,defaults={'rate_of_return' : rate_of_return , 'status_second': status_second, 'status_show' :status_show , 'payment_date' :payment_date , 'payback_period' : payback_period , 'period_length' : period_length } )
        serializer = serializers.InformationPlanSerializer(information)
        
       
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get(self,request,trace_code) : 
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan :
            return Response({'error': 'Invalid plan status'}, status=status.HTTP_400_BAD_REQUEST)
        information = InformationPlan.objects.filter(plan=plan).first()
        serializer = serializers.InformationPlanSerializer(information)
        return Response(serializer.data, status=status.HTTP_200_OK)


#done
class EndOfFundraisingViewset(APIView) :
    @method_decorator(ratelimit(**settings.RATE_LIMIT['POST']), name='post')
    def post (self,request,trace_code):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first() 
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan :
            return Response({'error': 'Invalid plan status'}, status=status.HTTP_400_BAD_REQUEST)
        information = InformationPlan.objects.filter(plan=plan).first()
        if not information:
            return Response({'error': 'information plan not found'}, status=status.HTTP_404_NOT_FOUND)
        date_payement = information.payment_date
        if isinstance(date_payement, str):
            date_payement = datetime.datetime.strptime(date_payement, '%Y-%m-%dT%H:%M:%S')
        if information.payback_period == '1':
            all_end_fundraising = []
            end_fundraising = EndOfFundraising.objects.filter(plan=plan)
            if not end_fundraising :
                return Response({'error': 'end of fundraising not found'}, status=status.HTTP_404_NOT_FOUND)        
            # EndOfFundraising.objects.filter(plan=plan).delete()
            data = request.data 
            updated_items=[]
            for item in data:
                fundraising_id = item.get('id')
                if fundraising_id is None:
                    return Response({'error': 'ID is required for each fundraising item'}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    fundraising_instance = EndOfFundraising.objects.get(id=fundraising_id, plan=plan)
                    fundraising_instance.amount_operator = item.get('amount_operator', fundraising_instance.amount_operator)
                    fundraising_instance.date_operator = item.get('date_operator', fundraising_instance.date_operator)
                    fundraising_instance.date_capitalization_operator = item.get(
                        'date_capitalization_operator', fundraising_instance.date_capitalization_operator
                    )
                    fundraising_instance.type = item.get('type', fundraising_instance.type)

                    fundraising_instance.save()

                    updated_items.append(fundraising_instance)

                except EndOfFundraising.DoesNotExist:
                    return Response({'error': f'Fundraising with ID {fundraising_id} not found.'}, 
                                    status=status.HTTP_404_NOT_FOUND)

            serializer = serializers.EndOfFundraisingSerializer(updated_items, many=True, partial=True)

            return Response({'date_payement' : serializer.data , 'date_start' : date_payement}, status=status.HTTP_200_OK)
        else:
            end_fundraising = EndOfFundraising.objects.filter(plan=plan)
            if not end_fundraising:
                return Response({'error': 'end of fundraising not found'}, status=status.HTTP_404_NOT_FOUND)
            data = request.data
            updated_items=[]
            for item in data:
                fundraising_id = item.get('id')
                if fundraising_id is None:
                    return Response({'error': 'ID is required for each fundraising item'}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    fundraising_instance = EndOfFundraising.objects.get(id=fundraising_id, plan=plan)
                    fundraising_instance.amount_operator = item.get('amount_operator', fundraising_instance.amount_operator)
                    fundraising_instance.date_operator = item.get('date_operator', fundraising_instance.date_operator)
                    fundraising_instance.date_capitalization_operator = item.get('date_capitalization_operator', fundraising_instance.date_capitalization_operator)
                    fundraising_instance.type = item.get('type', fundraising_instance.type)
                    fundraising_instance.save()
                    updated_items.append(fundraising_instance)
                except EndOfFundraising.DoesNotExist:
                    return Response({'error': f'Fundraising with ID {fundraising_id} not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = serializers.EndOfFundraisingSerializer(updated_items, many=True, partial=True)
            return Response({'date_payement' : serializer.data , 'date_start' : date_payement}, status=status.HTTP_200_OK)
    
    
    
    
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get(self,request,trace_code) : 
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first() 
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan :
            return Response({'error': 'Invalid plan status'}, status=status.HTTP_400_BAD_REQUEST)
        information = InformationPlan.objects.filter(plan=plan).first()
        if not information:
            return Response({'error': 'information plan not found'}, status=status.HTTP_404_NOT_FOUND)
        payback_period = information.payback_period
        date_payement = information.payment_date
        if isinstance(date_payement, str):
            date_payement = datetime.datetime.strptime(date_payement, '%Y-%m-%dT%H:%M:%S')
            
        end_fundraising = EndOfFundraising.objects.filter(plan=plan)
        if end_fundraising.exists():
            serializer = serializers.EndOfFundraisingSerializer(end_fundraising , many = True).data
            return Response({'date_payments' : serializer ,'date_start' :  date_payement}, status=status.HTTP_200_OK)
        if not end_fundraising.exists():
            if payback_period == '1':
                all_end_fundraising = []
                amount_fundraising = plan.sum_of_funding_provided
                if amount_fundraising:
                    amount_fundraising = amount_fundraising / 4
                else:
                    amount_fundraising = 0
                
                date = information.payment_date
                if date is None :
                    return Response({'error': 'payment date not found'}, status=status.HTTP_404_NOT_FOUND)
                if isinstance(date, str):
                    date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
                date = date + relativedelta(months=3) # از سه ماه اینده سود دهی شروع میشود

                for i in range(4):
                    format_date = date.strftime('%Y-%m-%d') # تاریخ سود 
                    date_capitalization = (date - timedelta(days=5)).date() #  تاریخ چک سود

                    end_fundraising = EndOfFundraising.objects.create(
                        plan=plan,
                        date_systemic=format_date,
                        date_operator=format_date,
                        amount_systemic=amount_fundraising,
                        amount_operator=amount_fundraising,
                        type=2,
                        date_capitalization_systemic=date_capitalization,
                        date_capitalization_operator=date_capitalization
                    )
                    all_end_fundraising.append(end_fundraising)
                    date = date + relativedelta(months=3)
                    last_calculated_date = date - relativedelta(months=3) # تاریخ چک اصل پول 
                    
                    date_capitalization_end = (last_calculated_date - timedelta(days=5)).date()
                end_fundraising_total = EndOfFundraising.objects.create(
                    plan=plan,
                    date_systemic=date_capitalization_end.strftime('%Y-%m-%d'),
                    date_operator=date_capitalization_end.strftime('%Y-%m-%d'),
                    amount_systemic=plan.sum_of_funding_provided,
                    amount_operator=plan.sum_of_funding_provided,
                    type=1,
                    date_capitalization_systemic=date_capitalization_end,
                    date_capitalization_operator=date_capitalization_end
                )
                
                all_end_fundraising.append(end_fundraising_total)
                serializer = serializers.EndOfFundraisingSerializer(all_end_fundraising, many=True)

                return Response({'date_payments' : serializer.data, 'date_start' : date_payement}, status=status.HTTP_200_OK)
            
            else :
                all_end_fundraising = []
                period_length = information.period_length
                amount_fundraising = plan.sum_of_funding_provided
                if not amount_fundraising:
                    amount_fundraising = 0
                
                date = information.payment_date
                if date is None :
                    return Response({'error': 'payment date not found'}, status=status.HTTP_404_NOT_FOUND)
                if isinstance(date, str):
                    date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
                date = date + relativedelta(months=period_length)
                format_date = date.strftime('%Y-%m-%d')
                date_capitalization = (date - timedelta(days=5)).date()
                end_fundraising = EndOfFundraising.objects.create(
                    plan=plan,
                    date_systemic=format_date,
                    date_operator=format_date,
                    amount_systemic=amount_fundraising,
                    amount_operator=amount_fundraising,
                    date_capitalization_systemic=date_capitalization,
                    date_capitalization_operator=date_capitalization,
                    type=2
                )
                all_end_fundraising.append(end_fundraising)
                end_fundraising_total =  EndOfFundraising.objects.create(
                    plan=plan,
                    date_systemic=format_date,
                    date_operator=format_date,
                    amount_systemic=amount_fundraising,
                    amount_operator=amount_fundraising,
                    date_capitalization_systemic=date_capitalization,
                    date_capitalization_operator=date_capitalization,
                    type=1
                )
                all_end_fundraising.append(end_fundraising_total)
                serializer = serializers.EndOfFundraisingSerializer(all_end_fundraising, many=True)
                return Response (serializer.data , status=status.HTTP_200_OK)
                

# done
class SendParticipationCertificateToFaraboursViewset(APIView):
    @method_decorator(ratelimit(**settings.RATE_LIMIT['POST']), name='post')
    def post(self, request, trace_code):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:
            return Response({'error': 'plan not found'}, status=status.HTTP_400_BAD_REQUEST)

        payment_ids = request.data.get('data')
        payments = PaymentGateway.objects.filter(plan=plan, id__in=payment_ids)
        if not payments:
            return Response({'error': 'چنین پرداختی یافت نشد'}, status=status.HTTP_400_BAD_REQUEST)
            
        for payment in payments:
            if payment.send_farabours:
                return Response({'error': 'پرداخت قبلا ارسال شده است'}, status=status.HTTP_400_BAD_REQUEST)
            if payment.status != '3':
                return Response({'error': 'پرداخت تایید نهایی نیست'}, status=status.HTTP_400_BAD_REQUEST)


            user_obj = User.objects.filter(uniqueIdentifier=payment.user).first()
            if not user_obj:
                return Response({'error': 'کاربر پرداخت کننده یافت نشد'}, status=status.HTTP_400_BAD_REQUEST)

            user_fname = get_fname(payment.user)
            user_lname = get_lname(payment.user)
            account_number = get_account_number(payment.user)
            mobile = get_mobile_number(payment.user)
            bourse_code = get_economi_code(payment.user)
            is_legal = check_legal_person(payment.user)
            payment_date = payment.create_date.strftime('%Y-%m-%d %H:%M:%S') if payment.create_date else None

            project_finance = ProjectFinancingProvider(
                projectID=trace_code,
                nationalID=payment.user,
                isLegal=is_legal,
                firstName=user_fname,
                lastNameOrCompanyName=user_lname,
                providedFinancePrice=payment.value,
                bourseCode=bourse_code,
                paymentDate=payment_date,
                shebaBankAccountNumber=account_number,
                mobileNumber=mobile,
                bankTrackingNumber=payment.track_id,
            )

            payment.send_farabours = True
            payment.save()
            apiFarabours = CrowdfundingAPI()
            response, status_code = apiFarabours.register_financing(project_finance)

            if status_code and status_code < 300:
                payment.trace_code_payment_farabourse = response.TraceCode
                payment.provided_finance_price_farabourse = response.ProvidedFinancePrice
                payment.message_farabourse = response.Message
                payment.error_no_farabourse = getattr(response, 'ErrorNo', None)
            else:
                payment.message_farabourse = getattr(response, 'ErrorMessage', 'Unknown error')
                payment.error_no_farabourse = getattr(response, 'ErrorNo', None)
                payment.send_farabours = False
            payment.save()

        return Response(True, status=status.HTTP_200_OK)

    @method_decorator(ratelimit(key='ip', rate='20/m', method='get', block=True))
    def get(self, request, trace_code):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        plan = Plan.objects.filter(trace_code = trace_code).first()
        if not plan :
            return Response({'error': 'plan not found '}, status=status.HTTP_400_BAD_REQUEST)
        
        payment = PaymentGateway.objects.filter(plan=plan , status = '3' )
        if not payment :
            return Response({'error': 'payment not found'}, status=status.HTTP_400_BAD_REQUEST)

        payment_serializer = serializers.PaymentGatewaySerializer(payment , many = True)
        if payment_serializer.data:
            payment_serializer = [
            {
                'id': item['id'],
                'plan': item['plan'],
                'status': item['status'],
                'document': item['document'],
                'send_farabours': item['send_farabours'],
                'trace_code_payment_farabourse': item['trace_code_payment_farabourse'],
                'provided_finance_price_farabourse': item['provided_finance_price_farabourse'],
                'message_farabourse': item['message_farabourse'],
                'error_no_farabourse': item['error_no_farabourse'],
                'track_id': item['track_id'],
                'amount': item['amount'],
                'value': item['value'],
                'create_date': item['create_date'],
                'user': item['user'],
                'user_name': get_name(item['user'])
            } for item in payment_serializer.data
        ] 
            
            
        return Response (payment_serializer , status=status.HTTP_200_OK)


# done
# save payment exel
class ShareholdersListExelViewset(APIView) :
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get(self, request, key):
        key_value = 'mahya1234'
        url_key = key  
        if url_key != key_value:
            return Response({'error': 'key is missing'}, status=status.HTTP_400_BAD_REQUEST)

        if request.FILES:
            file = request.FILES['file']
            df = pd.read_csv(file)



            # df['تعداد'] = df['مبلغ سفارش']/df['قیمت اسمی هر واحد']
            if not df.empty:
                for index, row in df.iterrows(): 
                    trace_code_values = row['شناسه طرح']
                    plan = Plan.objects.filter(trace_code= trace_code_values).first()
                
                    if not plan :
                        return Response({'error': f'plan not found {trace_code_values}'}, status=status.HTTP_400_BAD_REQUEST)
                    national_code = str(row['کد ملی']) if not pd.isna(row['کد ملی']) else ''
                    national_code = str(national_code).replace("'", "")
                    if row['روش پرداخت'] == 'اینترنتی' :
                        document = False
                    else :
                        document = True


                    # date_string = str(row['تاریخ سفارش']).strip()
                    # gregorian_date = datetime.datetime.strptime(date_string, '%d/%m/%Y %H:%M')


                    data = PaymentGateway.objects.update_or_create(
                        plan = plan,
                        user =str ( row['کد ملی']).replace("'", ""),
                        amount =  row['تعداد گواهی'],
                        value =  row['مبلغ سفارش'],
                        payment_id =  row['شناسه سفارش'],
                        document = document,
                        # create_date =  None,
                        risk_statement = True,
                        status =  '3',
                        send_farabours = True,
                        name_status = False,
                    )
# update information plan 
                df['مبلغ سفارش'] = df['مبلغ سفارش'].apply(int)
                value =df[['مبلغ سفارش','شناسه طرح']].groupby(by=['شناسه طرح']).sum()
                for i in value.index:
                    plan = Plan.objects.filter(trace_code= i).first()

                    if not plan :
                        return Response ({'error' :'Not Found  plan'} , status = status.HTTP_400_BAD_REQUEST)

                    information = InformationPlan.objects.filter(plan=plan).first()

                    if not information :
                        return Response ({'error' :'Not Found  planInformation'} , status = status.HTTP_400_BAD_REQUEST)
                    information.amount_collected_now = value['مبلغ سفارش'][i]
                    information.save()
                    

        return Response( True , status=status.HTTP_200_OK)


# done
# ضمانت نامه
class WarrantyAdminViewset(APIView) :
    @method_decorator(ratelimit(**settings.RATE_LIMIT['POST']), name='post')
    def post (self, request  ,*args, **kwargs) :
        trace_code = kwargs.get('key')
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        plan = Plan.objects.filter(trace_code = trace_code).first()
        if not plan :
            return Response({'error': 'plan not found '}, status=status.HTTP_400_BAD_REQUEST)
        date = request.data.get('date')
        if date == None :
            return Response({'error': 'date is required'}, status=status.HTTP_400_BAD_REQUEST)

        timestamp = int(date) / 1000
        date = datetime.datetime.fromtimestamp(timestamp)

        warranty = Warranty.objects.create(
            plan = plan,
            exporter = request.data.get('exporter'),
            date = date,
            completed = request.data.get('completed',False),
            comment = request.data.get('comment'),
            kind_of_warranty = request.data.get('kind_of_warranty'),
        )
        serializer = serializers.WarrantySerializer (warranty)

        return Response (serializer.data ,  status= status.HTTP_200_OK)
    
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get (self, request , *args, **kwargs):
        trace_code = kwargs.get('key')
        plan = Plan.objects.filter(trace_code = trace_code).first()
        warranties = Warranty.objects.filter(plan=plan)
        serializer = serializers.WarrantySerializer(warranties , many = True)
        return Response (serializer.data ,  status= status.HTTP_200_OK)

    
    @method_decorator(ratelimit(**settings.RATE_LIMIT['PATCH']), name='PATCH')
    def patch (self,request , *args, **kwargs):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        data = request.data
        
        warranties_id = data.get('id')
        if not warranties_id:
            return Response({'error': 'warranty ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        warranties = Warranty.objects.filter(id = warranties_id).first()
        if not warranties :
            return Response({'error': 'warranty not found '}, status=status.HTTP_400_BAD_REQUEST)
        if data.get('date'):
            try:
                timestamp = int(data['date']) / 1000
                data['date'] = datetime.datetime.fromtimestamp(timestamp)
                data['kind_of_warranty'] = request.data.get('kind_of_warranty')
                data['exporter'] = request.data.get('exporter')

            except (ValueError, TypeError):
                return Response({'error': 'Invalid date format'}, status=400)

        serializer = serializers.WarrantySerializer(warranties , data= data ,  partial = True )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data ,  status= status.HTTP_200_OK)
        return Response ({'message': 'update is not succsesfuly'} ,  status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(ratelimit(**settings.RATE_LIMIT['DELETE']), name='delete')
    def delete (self, request, *args, **kwargs):
        trace_code = kwargs.get('key')
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        plan = Plan.objects.filter(trace_code = trace_code).first()
        if not plan :
            return Response({'error': 'plan not found '}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        warranties_id = data.get('id')
        if not warranties_id:
            return Response({'error': 'warranty ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        warranties = Warranty.objects.filter(plan=plan , id = warranties_id).first()
        if not warranties :
            return Response({'error': 'warranty not found '}, status=status.HTTP_400_BAD_REQUEST)
        warranties.delete()
        return Response(True , status=status.HTTP_200_OK)


class WarrantyListAdminViewset(APIView):
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get(self, request):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        plans = {plan.id: plan for plan in Plan.objects.all()}  # ایجاد دیکشنری از اشیاء Plan با شناسه به عنوان کلید
        if not plans:
            return Response({'error': 'plan not found '}, status=status.HTTP_400_BAD_REQUEST)
        warranties = Warranty.objects.filter(plan__in=plans)
        if not warranties.exists():
            return Response({'error': 'No warranties found for the provided plans'},status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.WarrantySerializer(warranties, many=True).data
        df = pd.DataFrame(serializer)

        for i in serializer:
            date_str = i['date']
            try:
                date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f%z')
            except ValueError:
                try:
                    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
                except ValueError:
                    if '+' in date_str:
                        base_date, tz = date_str.split('+')
                        if ':' in tz and len(tz.replace(':', '')) > 4:
                            tz = tz[:5]
                            date_str = f"{base_date}+{tz}"
                            try:
                                date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
                            except ValueError:
                                date_obj = datetime.datetime.now()
                        else:
                            date_obj = datetime.datetime.now()
                    else:
                        date_obj = datetime.datetime.now()

            i['date'] = date_obj.strftime('%Y-%m-%d')
            plan_id = i['plan']
            if plan_id in plans:
                i['plan'] = plans[plan_id].persian_name
            else:
                i['plan'] = None

        return Response(serializer, status=status.HTTP_200_OK)
    
# done
# درگاه بانکی
class TransmissionViewset(APIView) : 
    @method_decorator(ratelimit(**settings.RATE_LIMIT['POST']), name='post')
    def post(self,request ,*args, **kwargs):
        trace_code = kwargs.get('key')
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_401_UNAUTHORIZED)
        user = user.first()
        legal_user = check_legal_person(user.uniqueIdentifier)

        plan = Plan.objects.filter(trace_code=trace_code).first()
        plan_unit_price = plan.unit_price #قیمت هر سهم به ریال 
        information_plan = InformationPlan.objects.filter(plan=plan).first()

        value = request.data.get('amount')  # مبلغ درخواستی کاربر برای خرید
        if not value:
            value = 0
        try:
            value = int(value)
        except ValueError:
            return Response({'error': 'مبلغ باید عدد صحیح باشد'}, status=status.HTTP_400_BAD_REQUEST)
        value = int(value)
        all_value = PaymentGateway.objects.filter(plan=plan,user=user.uniqueIdentifier,status__in=['2','3','1']).aggregate(Sum('value'))['value__sum'] or 0
        all_value = value + all_value        
        if value is None:
            value = 0    
        amount_collected_now = information_plan.amount_collected_now # مبلغ جمه اوری شده تا به  الان
        plan_total_price = plan.total_units # کل سهم قابل عرضه برای طرح 
        purchaseable_amount = int((plan_total_price*plan_unit_price) - amount_collected_now) # مبلغ قابل خرید همه کاربران 
        if value > purchaseable_amount :
            return Response({'error': 'مبلغ بیشتر از سهم قابل خرید است'}, status=status.HTTP_400_BAD_REQUEST)
        if legal_user == True : 
            amount_legal_min = plan.legal_person_minimum_availabe_price #حداقل سهم قابل خرید حقوقی 
            amount_legal_max = plan.legal_person_maximum_availabe_price #حداکثر سهم قابل خرید حقوقی
            if not amount_legal_min :
                amount_legal_min = plan_unit_price
            if not amount_legal_max :
                amount_legal_max = purchaseable_amount

            if value < amount_legal_min :
                return Response({'error': 'مبلغ  کمتر از  حد مجاز قرارداد شده است'}, status=status.HTTP_400_BAD_REQUEST)
            if all_value > amount_legal_max:
                return Response({'error': 'مبلغ بیشتراز  حد مجاز قرارداد شده است'}, status=status.HTTP_400_BAD_REQUEST)

            
            if value > purchaseable_amount :
                return Response({'error': 'مبلغ بیشتر از سهم قابل خرید است'}, status=status.HTTP_400_BAD_REQUEST)
                
                
        else :
            amount_personal_min = plan.real_person_minimum_availabe_price  #حداقل سهم قابل خرید حقیقی
            amount_personal_max = plan.real_person_maximum_available_price #حداکثر سهم قابل خرید حقیقی

            if not amount_personal_min :
                amount_personal_min = plan_unit_price

            if not amount_personal_max :
                amount_personal_max = purchaseable_amount

            if value < amount_personal_min :
                return Response({'error': 'مبلغ   کمتر از  حد مجاز قرارداد شده است'}, status=status.HTTP_400_BAD_REQUEST)
            if all_value > amount_personal_max :
                return Response({'error': 'مبلغ بیشتر از  حد مجاز قرارداد شده است'}, status=status.HTTP_400_BAD_REQUEST)
        
            else :
                if value > purchaseable_amount :
                    return Response({'error': 'مبلغ بیشتر از سهم قابل خرید است'}, status=status.HTTP_400_BAD_REQUEST)
                  

            
        user = User.objects.filter(uniqueIdentifier = user.uniqueIdentifier).first()
        full_name = get_name(user.uniqueIdentifier)
        
        pep = PasargadPaymentGateway()
        invoice_data = {
            'invoice' : pep.generator_invoice_number(),
            'invoiceDate': pep.generator_date(),
            
        }
        description_user = request.data.get('description_user','')
        description = f"مشارکت در طرح {plan.persian_name} به مبلغ {value} ریال | {description_user}"
        created = pep.create_purchase(
            invoice  = invoice_data['invoice'],
            invoiceDate = invoice_data['invoiceDate'],
            amount = value ,
            callback_url = os.getenv('callback_url'),
            mobile_number = user.mobile,
            service_code =  '8' ,
            payerName = full_name,
            nationalCode = user.uniqueIdentifier,
            description = description
        )
        payment = PaymentGateway.objects.create(
            plan = plan,
            user = user.uniqueIdentifier,
            amount = int(value / plan.unit_price),
            value = value,
            payment_id = invoice_data['invoice'],
            description = description,
            code = None,
            risk_statement = True,
            status = '1',
            document = False,
            picture = None , 
            send_farabours = False,
            url_id = created['urlId'] , 
            mobile = user.mobile,
            invoice = invoice_data['invoice'],
            name = get_name(user.uniqueIdentifier),
            service_code = '8',
            name_status = request.data.get('name_status')
        )
        payment.save()

        return Response({'url' : created['url'] }, status=status.HTTP_200_OK)
    
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    @transaction.atomic
    def get (self,request,*args, **kwargs):
        # Authorization = request.headers.get('Authorization')
        # if not Authorization:
        #     return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        # user = fun.decryptionUser(Authorization)
        # if not user:
        #     return Response({'error': 'user not found'}, status=status.HTTP_401_UNAUTHORIZED)
        # user = user.first()
        
        pep = PasargadPaymentGateway()
        invoice = kwargs.get('key')
        payment = PaymentGateway.objects.filter(invoice = invoice).first()
        
        if not payment :
            return Response({'error': 'payment not found'}, status=status.HTTP_400_BAD_REQUEST)
        try :
            pep = pep.confirm_transaction(payment.invoice , payment.url_id)
        except Exception as e:
            print('error in confirm transaction')
            print(e)
            payment.status = '1'
            payment.save()
            return Response({'error':'payment not found'}, status=status.HTTP_400_BAD_REQUEST)
        payment.status = '2'
        try :
            payment.reference_number = pep['referenceNumber']
            payment.track_id = pep['trackId']
            payment.card_number = pep['maskedCardNumber']
        except :
            pass
        payment.save()
        try :
            payment_value = PaymentGateway.objects.filter(plan=payment.plan)
            serializer = serializers.PaymentGatewaySerializer(payment_value , many = True)
            payment_df = pd.DataFrame(serializer.data)
            payment_df = payment_df[payment_df['status'] != '0'] 
            payment_df = payment_df[payment_df['status'] != '1'] 
            payment_value = payment_df['value'].sum()
            plan = Plan.objects.filter(id=payment.plan).first()
            information = InformationPlan.objects.filter(plan=plan).first()
            information.amount_collected_now = payment_value
            information.save()
        except:
            pass
        return Response(True , status=status.HTTP_200_OK)

# فیش بانکی های کاربر
class BankReceiptViewset(APIView):
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get (self,request,id):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        payment = PaymentGateway.objects.filter (id=id)
        if not payment :
            return Response({'error': 'payment not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.PaymentGatewaySerializer(payment , many = True)
        return Response (serializer.data,status=status.HTTP_200_OK)

# گواهی مشارکت منو 
class ParticipantMenuViewset(APIView):
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get (self,request):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_401_UNAUTHORIZED)
        user = user.first()
        # payment = PaymentGateway.objects.filter(user=user, send_farabours =True , status = '3').distinct()
        payment = PaymentGateway.objects.filter(user=user.uniqueIdentifier, status = '3')
        serializer = serializers.PaymentGatewaySerializer(payment,many = True)
        plans = []
        for i in serializer.data :
            plan = i['plan']
            plan = Plan.objects.filter(id=plan).first()
            if not plan :
                return Response({'error': 'plan not found'}, status=status.HTTP_404_NOT_FOUND)
            
            information = InformationPlan.objects.filter(plan =plan , status_second ='5').first()
            if not information :
                continue
            
            if plan not in plans:
                plans.append(plan) 

        plan_serializer = serializers.PlanSerializer(plans, many=True)
        return Response (plan_serializer.data,status=status.HTTP_200_OK)
    
       
class RoadMapViewset(APIView) :
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get (self,request,id) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_401_UNAUTHORIZED)
        user = user.first()
        cart = Cart.objects.filter(user=user).first()
        if not cart :
            return Response ({'error': 'Cart not found'}, status=status.HTTP_400_BAD_REQUEST)
        plan = Plan.objects.filter(id=id).first()
        if not plan :
            return Response ({'error': 'plan not found'}, status=status.HTTP_400_BAD_REQUEST)
        date_cart = cart.creat
        date_plan = None
        date_end_plan = None
        date_contract = None
        list = {
            'date_cart' : date_cart,
            'date_plan' : '2024-09-24T08:44:41.701688Z',
            'date_end_plan' : '2024-09-24T08:44:41.701688Z',
            'date_contract' : '2024-09-24T08:44:41.701688Z'
        }
            
        

        return Response({'data': list}, status=status.HTTP_200_OK)


class PaymentInquiryViewSet(APIView) :
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def post (self,request,trace_code) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan :
            return Response ({'error': 'plan not found'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data.get('id')
        payment = PaymentGateway.objects.filter(plan = plan , id = data ).first()
        if not payment:
            return Response({'error': 'payment not found'}, status=status.HTTP_400_BAD_REQUEST)
        payment_invoices = payment.payment_id
        pep = PasargadPaymentGateway()
        payment_inquiry = pep.inquiry_transaction(invoice=payment_invoices)
        
        try :
            if  payment.reference_number != payment_inquiry['referenceNumber'] :
                payment.reference_number = payment_inquiry['referenceNumber']
        except :
            pass
        try :   
            if payment.track_id != payment_inquiry['trackId']:
                payment.track_id = payment_inquiry['trackId']
        except :
            pass

        try:
            if payment.code_status_payment != payment_inquiry['status']:
                payment.code_status_payment = payment_inquiry['status']
        except:
            pass

        try:
            if payment.card_number != payment_inquiry['cardNumber']:
                payment.card_number = payment_inquiry['cardNumber']
        except:
            pass

        payment.save()
        return Response(True, status=status.HTTP_200_OK)


class SendParticipationNotificationViewset (APIView):
    @method_decorator(ratelimit(**settings.RATE_LIMIT['POST']), name='post')
    def post (self,request,trace_code):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan :
            return Response({'error': 'plan not found'}, status=status.HTTP_400_BAD_REQUEST)
        payment = PaymentGateway.objects.filter(plan=plan , status = '3' , send_farabours = True)
        if not payment :
            return Response({'error': 'payment not found'}, status=status.HTTP_400_BAD_REQUEST)
        information = InformationPlan.objects.filter(plan=plan , status_second ='5').first()
        if not information :
            return Response({'error': 'information plan not found'}, status=status.HTTP_400_BAD_REQUEST)
        payment = payment.distinct('user')
        
        for i in payment :
            user = User.objects.filter(uniqueIdentifier=i.user).first()
            user_notifier = UserNotifier(user.mobile , user.email)
            user_notifier.send_finance_completion_email(payment.value)
        user_notifier = UserNotifier(payment.mobile , payment.email)
        
        
class CheckVerificationPaymentAdminViewset (APIView):
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get (self,request):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()

        end_of_fundraising = EndOfFundraising.objects.all()

        if not end_of_fundraising :
            return Response({'error': 'end of fundraising not found'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.EndOfFundraisingSerializer(end_of_fundraising, many=True).data
        listPayment = []
        for i in serializer :
            plan = Plan.objects.filter(id=i['plan']).first()
            date_operator = i['date_operator']
            try:
                date_operator = datetime.datetime.strptime(date_operator, '%Y-%m-%dT%H:%M:%S%z')
            except ValueError:
                date_operator = datetime.datetime.strptime(date_operator, '%Y-%m-%d')          
            date_operator = JalaliDate.to_jalali(date_operator.year, date_operator.month, date_operator.day)
            date_operator = date_operator.strftime('%Y-%m-%d')

            date_capitalization_operator = i['date_capitalization_operator']
            try:
                date_capitalization_operator = datetime.datetime.strptime(date_capitalization_operator, '%Y-%m-%dT%H:%M:%S%z')
            except ValueError:
                date_capitalization_operator = datetime.datetime.strptime(date_capitalization_operator, '%Y-%m-%d')          
            date_capitalization_operator = JalaliDate.to_jalali(date_capitalization_operator.year, date_capitalization_operator.month, date_capitalization_operator.day)
            date_capitalization_operator = date_capitalization_operator.strftime('%Y-%m-%d')
            serializer ={
                'id': i['id'],
                'plan': plan.persian_suggested_symbol,
                'amount_operator': i['amount_operator'],
                'date_operator': date_operator,
                'date_capitalization_operator': date_capitalization_operator,
                'profit_payment_comment' : i['profit_payment_comment'],
                'profit_payment_completed': i['profit_payment_completed'],
            }
            listPayment.append(serializer)
        return Response(listPayment, status=status.HTTP_200_OK)
        
    @method_decorator(ratelimit(**settings.RATE_LIMIT['PATCH']), name='PATCH')
    def patch (self,request):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        id = request.data.get('id')

        end_of_fundraising = EndOfFundraising.objects.filter(id=id).first()
        if not end_of_fundraising :
            return Response({'error': 'end of fundraising not found'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        end_of_fundraising.profit_payment_comment = data.get('profit_payment_comment','')
        end_of_fundraising.profit_payment_completed = data.get('profit_payment_completed',False)
        end_of_fundraising.save()
        return Response(True, status=status.HTTP_200_OK)
       

class CheckVerificationReceiptAdminViewset (APIView):
    @method_decorator(ratelimit(**settings.RATE_LIMIT['GET']), name='get')
    def get (self,request):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        end_of_fundraising = EndOfFundraising.objects.all()
        if not end_of_fundraising :
            return Response({'error': 'end of fundraising not found'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.EndOfFundraisingSerializer(end_of_fundraising, many=True).data

        listPayment = []
        for i in serializer :
            plan = Plan.objects.filter(id=i['plan']).first()
            date_operator = i['date_operator']
            try:
                date_operator = datetime.datetime.strptime(date_operator, '%Y-%m-%dT%H:%M:%S%z')
            except ValueError:
                date_operator = datetime.datetime.strptime(date_operator, '%Y-%m-%d')          
            date_operator = JalaliDate.to_jalali(date_operator.year, date_operator.month, date_operator.day)
            date_operator = date_operator.strftime('%Y-%m-%d')

            date_capitalization_operator = i['date_capitalization_operator']
            try:
                date_capitalization_operator = datetime.datetime.strptime(date_capitalization_operator, '%Y-%m-%dT%H:%M:%S%z')
            except ValueError:
                date_capitalization_operator = datetime.datetime.strptime(date_capitalization_operator, '%Y-%m-%d')          
            date_capitalization_operator = JalaliDate.to_jalali(date_capitalization_operator.year, date_capitalization_operator.month, date_capitalization_operator.day)
            date_capitalization_operator = date_capitalization_operator.strftime('%Y-%m-%d')

            serializer ={
                'id': i['id'],
                'plan': plan.persian_suggested_symbol,
                'amount_operator': i['amount_operator'],
                'date_operator': date_operator,
                'date_capitalization_operator': date_capitalization_operator,
                'profit_receipt_comment' : i['profit_receipt_comment'],
                'profit_receipt_completed': i['profit_receipt_completed'],
            }
            listPayment.append(serializer)
        return Response(listPayment, status=status.HTTP_200_OK)
    
    @method_decorator(ratelimit(key='ip', rate='25/m', method='PATCH', block=True))
    def patch (self,request):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        id = request.data.get('id')
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_401_UNAUTHORIZED)
        admin = admin.first()
        end_of_fundraising = EndOfFundraising.objects.filter(id=id).first()
        if not end_of_fundraising :
            return Response({'error': 'end of fundraising not found'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        end_of_fundraising.profit_receipt_comment = data.get('profit_receipt_comment','')
        end_of_fundraising.profit_receipt_completed = data.get('profit_receipt_completed',False)
        end_of_fundraising.save()
        return Response(True, status=status.HTTP_200_OK)
            
        
class ComplaintViewset (APIView):
    @method_decorator(ratelimit(**settings.RATE_LIMIT['POST']), name='post')
    def post (self,request,trace_code):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_401_UNAUTHORIZED)
        user = user.first()
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan :
            return Response({'error': 'plan not found'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        complaint = Complaint.objects.create(
            plan=plan, 
            user=user,
            title=data.get('title'), 
            description=data.get('description') , 
            send_farabourse = data.get('send_farabourse',False), 
            message = data.get('message')
            )
        serializer = serializers.ComplaintSerializer(complaint).data

        return Response(serializer, status=status.HTTP_200_OK)
        

    def get (self,request,trace_code):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_401_UNAUTHORIZED)
        user = user.first()
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan :
            return Response({'error': 'plan not found'}, status=status.HTTP_400_BAD_REQUEST)
        complaint = Complaint.objects.filter(user=user, plan=plan)
        serializer = serializers.ComplaintSerializer(complaint, many=True).data

        return Response(serializer, status=status.HTTP_200_OK)


