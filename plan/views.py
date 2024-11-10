from .models import Plan , DocumentationFiles ,Appendices ,Comment  , Plans ,ListOfProjectBoardMembers,ProjectOwnerCompan , PaymentGateway ,PicturePlan ,Warranty, InformationPlan , EndOfFundraising ,ListOfProjectBigShareHolders
from rest_framework.response import Response
from rest_framework import status 
from rest_framework.views import APIView
from authentication import fun
from . import serializers
from investor.models import Cart
from authentication.models import privatePerson , User , accounts , LegalPerson , tradingCodes
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
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit   
from django.utils.decorators import method_decorator



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
    privateperson = privatePerson.objects.filter(user=user).first()
    first_name = privateperson.firstName
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
    economi_code = economi_code.code
    return economi_code


def get_account_number(uniqueIdentifier) :
    user = User.objects.filter(uniqueIdentifier=uniqueIdentifier).first()
    user_account = accounts.objects.filter(user=user).first()
    sheba = user_account.sheba
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


class PlanViewset(APIView):
    """
    This view provides detailed information about a specific plan, including plan details, board members, shareholders,
    associated companies, and fundraising end dates, all identified by the plan's unique trace code.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get(self, request, trace_code):
        """
        Retrieve detailed information for a specific plan by trace code.

        This method retrieves comprehensive details about a plan, including board members, shareholders, the associated company,
        and fundraising dates in both Gregorian and Jalali formats. The information includes both the plan's primary details 
        and additional information such as start dates and end of fundraising information.

        - If the plan with the specified trace code does not exist, a "Plan not found" message is returned.

        Parameters:
            - trace_code (str, path): Unique identifier for the plan.

        Responses:
            200: {
                "plan": {
                    "trace_code": <trace_code>,
                    "title": <plan_title>,
                    ...
                },
                "board_member": [
                    {
                        "first_name": <member_first_name>,
                        "last_name": <member_last_name>,
                        "organization_post_description": <post_description>,
                        ...
                    },
                    ...
                ],
                "shareholder": [
                    {
                        "share_percent": <share_percentage>,
                        "first_name": <shareholder_first_name>,
                        "last_name": <shareholder_last_name>,
                        ...
                    },
                    ...
                ],
                "company": [
                    {
                        "company_name": <company_name>,
                        "company_national_id": <company_national_id>,
                        ...
                    },
                    ...
                ],
                "picture_plan": {
                    "image_url": <image_url>,
                    ...
                },
                "information_complete": {
                    "payment_date": <start_date>,
                    ...
                },
                "date_start": <start_date>,
                "date_profit": [
                    {
                        "type": <profit_type>,
                        "date": <jalali_date>
                    },
                    ...
                ]
            }
            404: {"message": "Plan not found"}
        """
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:
            return Response({'message': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)
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
        

class PlansViewset(APIView):
    """
    This view provides a list of all plans with their associated information and allows updating of plan details by fetching 
    and syncing data from an external API.
    """
    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get(self, request):
        """
        Retrieve a list of all plans along with detailed associated information.

        This method retrieves all available plans along with their respective information, including board members, 
        shareholders, associated companies, and plan pictures.

        Responses:
            200: [
                {
                    "plan": {
                        "trace_code": <trace_code>,
                        "title": <plan_title>,
                        ...
                    },
                    "board_members": [
                        {
                            "first_name": <member_first_name>,
                            "last_name": <member_last_name>,
                            "organization_post_description": <post_description>,
                            ...
                        },
                        ...
                    ],
                    "shareholder": [
                        {
                            "share_percent": <share_percentage>,
                            "first_name": <shareholder_first_name>,
                            "last_name": <shareholder_last_name>,
                            ...
                        },
                        ...
                    ],
                    "company": [
                        {
                            "company_name": <company_name>,
                            "company_national_id": <company_national_id>,
                            ...
                        },
                        ...
                    ],
                    "picture_plan": {
                        "image_url": <image_url>,
                        ...
                    },
                    "information_complete": {
                        "payment_date": <start_date>,
                        ...
                    }
                },
                ...
            ]
        """
        plans = Plan.objects.all()
        result = []

        for plan in plans:
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
   

    @method_decorator(ratelimit(key='ip', rate='5/m', method='PATCH', block=True))
    def patch(self, request):
        """
        Update plans by syncing data from an external API.

        This method authenticates the admin using the Authorization header and synchronizes plan details by fetching data 
        from an external API. It updates existing plans or creates new ones if they do not already exist.

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.

        Parameters:
            - Authorization (str, header): Admin's authorization token.

        Responses:
            200: {"message": "بروزرسانی از فرابورس انجام شد"}
            400: {"error": "Authorization header is missing"}
            404: {"error": "admin not found"}
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
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
                    'number_of_finance_provider': plan_detail.get('Number of Finance Provider', None),
                    'sum_of_funding_provided': plan_detail.get('SumOfFundingProvided', None)
                }
            )
            print()


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


class AppendicesViewset(APIView) :
    """
    This view allows admins to upload, retrieve, and delete appendices associated with a specific plan, identified by the plan's trace code.
    """
    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post (self,request,trace_code) :
        """
        Upload an appendix file for a specific plan.

        This method authenticates the admin using the Authorization header and allows them to upload a new appendix 
        file associated with a plan identified by its trace code.

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - If the plan with the specified trace code does not exist, an error is returned.
        - If the file data is invalid or missing, an error is returned.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - trace_code (str, path): Unique identifier for the plan.
            - file (file, form-data): The file to be uploaded as an appendix.

        Responses:
            200: {
                "id": <appendix_id>,
                "file": <file_url>,
                "description": <description>,
                ...
            }
            400: {"error": "Authorization header is missing" / "File data is invalid"}
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
        serializer = serializers.AppendicesSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if 'file' in request.FILES:
            serializer.uploaded_file = request.FILES['file']
        serializer.save(plan=plan)
        return Response (serializer.data, status=status.HTTP_200_OK)
    
    
    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get (self,request,trace_code) :
        """
        Retrieve all appendix files for a specific plan.

        This method retrieves all appendices associated with a plan identified by its trace code. It returns 
        information for each appendix file including file URLs and descriptions.

        - If the plan with the specified trace code does not exist, an error is returned.
        - If no appendices are found for the specified plan, an error is returned.

        Parameters:
            - trace_code (str, path): Unique identifier for the plan.

        Responses:
            200: [
                {
                    "id": <appendix_id>,
                    "file": <file_url>,
                    "description": <description>,
                    ...
                },
                ...
            ]
            404: {"error": "Plan not found" / "Appendices not found"}
        """
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:
            return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)
        appendices = Appendices.objects.filter(plan=plan)
        if not appendices.exists() :
            return Response({'error': 'Appendices not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.AppendicesSerializer(appendices, many= True)
        return Response(serializer.data , status=status.HTTP_200_OK)
    
    
    @method_decorator(ratelimit(key='ip', rate='5/m', method='DELETE', block=True))
    def delete(self,request,trace_code):
        """
        Delete a specific appendix by its ID.

        This method authenticates the admin using the Authorization header and deletes an appendix identified by 
        its unique ID. 

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - If the appendix with the specified ID does not exist, an error is returned.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - trace_code (int, path): Unique identifier for the appendix.

        Responses:
            200: {"message": "success"}
            400: {"error": "Authorization header is missing"}
            404: {"error": "admin not found" / "Appendices not found"}
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        appendices = Appendices.objects.filter(id=int(trace_code))
        if not appendices.exists() :
            return Response({'error': 'Appendices not found'}, status=status.HTTP_404_NOT_FOUND)
        appendices.delete()
        return Response({'message':'succes'} , status=status.HTTP_200_OK)


class DocumentationViewset(APIView) :
    """
    This view allows admins to upload, retrieve, and delete documentation files associated with a specific plan, identified by the plan's trace code.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request, trace_code):
        """
        Upload a documentation file for a specific plan.

        This method authenticates the admin using the Authorization header and allows them to upload a new documentation 
        file associated with a plan identified by its trace code.

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - If the plan with the specified trace code does not exist, an error is returned.
        - If the file data is invalid or missing, an error is returned.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - trace_code (str, path): Unique identifier for the plan.
            - file (file, form-data): The file to be uploaded as documentation.

        Responses:
            200: {
                "data": {
                    "id": <documentation_id>,
                    "file": <file_url>,
                    "description": <description>,
                    ...
                }
            }
            400: {"error": "Authorization header is missing" / "File data is invalid"}
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
        serializer = serializers.DocumentationSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if 'file' in request.FILES:
            serializer.uploaded_file = request.FILES['file']



        serializer.save(plan=plan)
        return Response ({'data' : serializer.data} , status=status.HTTP_200_OK)
    
    
    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get (self,request,trace_code) :
        """
        Retrieve all documentation files for a specific plan.

        This method retrieves all documentation files associated with a plan identified by its trace code. 
        Each file entry includes its URL, description, and other metadata.

        - If the plan with the specified trace code does not exist, an error is returned.

        Parameters:
            - trace_code (str, path): Unique identifier for the plan.

        Responses:
            200: [
                {
                    "id": <documentation_id>,
                    "file": <file_url>,
                    "description": <description>,
                    ...
                },
                ...
            ]
            404: {"error": "Plan not found"}
        """

        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:
            return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)
        ducumentation = DocumentationFiles.objects.filter(plan=plan)
        serializer = serializers.DocumentationSerializer(ducumentation, many= True)
        return Response(serializer.data , status=status.HTTP_200_OK)
    
    
    @method_decorator(ratelimit(key='ip', rate='5/m', method='DELETE', block=True))
    def delete(self,request,trace_code):
        """
        Delete a specific documentation file by its ID.

        This method authenticates the admin using the Authorization header and deletes a documentation file identified by 
        its unique ID. 

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - If the documentation file with the specified ID does not exist, an error is returned.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - trace_code (int, path): Unique identifier for the documentation file.

        Responses:
            200: {"message": "success"}
            400: {"error": "Authorization header is missing"}
            404: {"error": "admin not found" / "Appendices not found"}
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        appendices = DocumentationFiles.objects.filter(id=int(trace_code))
        if not appendices.exists() :
            return Response({'error': 'Appendices not found'}, status=status.HTTP_404_NOT_FOUND)
        appendices.delete()
        return Response({'message':'succses'} , status=status.HTTP_200_OK)
    

class CommentAdminViewset(APIView):
    """
    This view allows admins to retrieve and update comments associated with a specific plan, identified by the plan's trace code.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get(self, request, trace_code):
        """
        Retrieve all comments for a specific plan.

        This method authenticates the admin using the Authorization header and retrieves all comments associated with a 
        plan identified by its trace code. If a comment has no answer, it is marked as "Awaiting Response" and saved.

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - If the plan with the specified trace code does not exist, an error is returned.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - trace_code (str, path): Unique identifier for the plan.

        Responses:
            200: [
                {
                    "id": <comment_id>,
                    "content": <comment_content>,
                    "answer": <answer>,
                    "date_created": <date>,
                    ...
                },
                ...
            ]
            400: {"error": "Authorization header is missing"}
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

        comments = Comment.objects.filter(plan=plan)
        for comment in comments:
            if comment.answer is None or comment.answer == '':
                comment.answer = 'منتظر پاسخ'
                comment.save()  

        serializer = serializers.CommenttSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    @method_decorator(ratelimit(key='ip', rate='5/m', method='PATCH', block=True))
    def patch (self,request,trace_code) :
        """
        Update a specific comment by adding or modifying its answer.

        This method authenticates the admin using the Authorization header and allows them to update the answer for 
        a specific comment identified by its unique ID. If no answer is provided, it defaults to "Awaiting Response".

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - If the comment with the specified ID does not exist, an error is returned.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - trace_code (int, path): Unique identifier for the comment.
            - answer (str, body): The answer to the comment (optional, defaults to "Awaiting Response").

        Responses:
            200: {
                "id": <comment_id>,
                "content": <comment_content>,
                "answer": <updated_answer>,
                "date_created": <date>,
                ...
            }
            400: {"error": "Authorization header is missing"}
            404: {"error": "admin not found" / "Comment not found"}
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
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


class CommentViewset(APIView):
    """
    This view allows authenticated users to post and retrieve comments associated with a specific plan, identified by the plan's trace code.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request, trace_code):
        """
        Submit a new comment for a specific plan.

        This method authenticates the user using the Authorization header and allows them to submit a comment associated with a plan 
        identified by its trace code. Comments are initially marked as "Awaiting Response" for the answer.

        - If the Authorization header is missing, an error is returned.
        - If the user's authorization token is invalid or the user is not found, an error is returned.
        - If the plan with the specified trace code does not exist, an error is returned.
        - If the comment text is missing, an error is returned.

        Parameters:
            - Authorization (str, header): User's authorization token.
            - trace_code (str, path): Unique identifier for the plan.
            - known (bool, body): Indicates if the comment is anonymous (optional, defaults to False).
            - comment (str, body): The text of the comment.

        Responses:
            200: True
            400: {"error": "Authorization header is missing"}
            404: {"error": "user not found" / "plan not found" / "Comment not found"}
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
        data = request.data.copy()
        if not data['known']:
            data['known'] = False
        if not data['comment']:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
        comment = Comment(plan=plan , user=user, known=data['known'] ,comment= data['comment'] ,answer='منتظر پاسخ')
        comment.save()
        return Response(True,status=status.HTTP_200_OK)
    
    
    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get (self,request,trace_code) :
        """
        Retrieve all approved comments for a specific plan.

        This method authenticates the user using the Authorization header and retrieves all comments associated with 
        a plan identified by its trace code that have been marked as approved (status=True).

        - If the Authorization header is missing, an error is returned.
        - If the user's authorization token is invalid or the user is not found, an error is returned.
        - If the plan with the specified trace code does not exist, an error is returned.
        - If no approved comments exist for the specified plan, an error is returned.

        Parameters:
            - Authorization (str, header): User's authorization token.
            - trace_code (str, path): Unique identifier for the plan.

        Responses:
            200: [
                {
                    "id": <comment_id>,
                    "user": <user_id>,
                    "comment": <comment_text>,
                    "answer": <answer>,
                    "date_created": <date>,
                    ...
                },
                ...
            ]
            400: {"error": "Authorization header is missing"}
            404: {"error": "user not found" / "Plan not found" / "privatePerson not found" / "comments not found or no status true"}
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
            return Response({'error': 'Plan not found'}, status=status.HTTP_400_BAD_REQUEST)

        private_person = privatePerson.objects.filter(user=user).first()
        if not private_person:
            return Response({'error': 'privatePerson not found'}, status=status.HTTP_404_NOT_FOUND)

        comments = Comment.objects.filter(plan=plan, status=True)
        if not comments.exists():
            return Response({'error': 'comments not found or no status true'}, status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.CommenttSerializer(comments, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

class SendpicturePlanViewset(APIView):
    """
    This view allows admins to upload and retrieve the picture associated with a specific plan, identified by the plan's trace code.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request, trace_code):
        """
        Upload or update a picture for a specific plan.

        This method authenticates the admin using the Authorization header and allows them to upload a picture 
        associated with a plan identified by its trace code. If a picture already exists, it is replaced.

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - If the plan with the specified trace code does not exist, an error is returned.
        - If no picture file is uploaded, an error is returned.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - trace_code (str, path): Unique identifier for the plan.
            - picture (file, form-data): The picture file to be uploaded.

        Responses:
            200: {
                "success": True,
                "message": "Picture updated successfully"
            }
            400: {"error": "Authorization header is missing" / "No picture file was uploaded"}
            404: {"error": "admin not found" / "plan not found"}
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
            return Response({'error': 'plan not found'}, status=status.HTTP_404_NOT_FOUND)
        if 'picture' not in request.FILES:
            return Response({'error': 'No picture file was uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        picture = PicturePlan.objects.filter(plan=plan).first()
        if picture :
            picture.delete()
        picture = PicturePlan.objects.create(plan=plan , picture = request.FILES['picture'])
        picture.save()
        return Response({'success': True, 'message': 'Picture updated successfully'}, status=status.HTTP_200_OK)


    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get (self,request,trace_code) :
        """
        Retrieve the picture associated with a specific plan.

        This method retrieves the picture associated with a plan identified by its trace code. It returns the picture's 
        file URL and other metadata.

        - If the plan with the specified trace code does not exist, an error is returned.

        Parameters:
            - trace_code (str, path): Unique identifier for the plan.

        Responses:
            200: {
                "id": <picture_id>,
                "picture": <picture_url>,
                ...
            }
            404: {"error": "plan not found"}
        """
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:
            return Response({'error': 'plan not found'}, status=status.HTTP_404_NOT_FOUND)
        picture = PicturePlan.objects.filter(plan=plan).first()
        serializer = serializers.PicturePlanSerializer(picture)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PaymentDocument(APIView):
    """
    This view allows authenticated users to create, retrieve, and update payment documents for a specific plan, identified by the plan's trace code.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request, trace_code):
        """
        Create a new payment document for a specific plan.

        This method authenticates the user using the Authorization header and allows them to create a payment document 
        for a plan identified by its trace code. The document includes details like the amount, payment ID, picture, and risk statement acknowledgment.

        - If the Authorization header is missing, an error is returned.
        - If the user's authorization token is invalid or the user is not found, an error is returned.
        - If the plan with the specified trace code does not exist, an error is returned.
        - If the purchase amount exceeds available units or is outside permissible limits, an error is returned.
        - Required fields like amount, payment ID, and risk statement must be provided.

        Parameters:
            - Authorization (str, header): User's authorization token.
            - trace_code (str, path): Unique identifier for the plan.
            - amount (int, body): The number of units requested by the user.
            - payment_id (str, body): Unique identifier for the payment transaction.
            - description (str, body, optional): Additional payment description.
            - risk_statement (bool, body): Acknowledgment of the risk statement (must be true).
            - name_status (bool, body): Indicates if the user's name can be displayed.
            - picture (file, form-data): Picture file of the payment document.

        Responses:
            200: "success"
            400: {"error": "Authorization header is missing" / "amount not found" / "mismatched amount or risk statement not true"}
            404: {"error": "user not found" / "plan not found" / "payment_id not found"}
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
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
        plan_total_price = plan.total_units # کل سهم قابل عرضه برای طرح 
        purchaseable_amount = int(plan_total_price - amount_collected_now) # مبلغ قابل خرید همه کاربران 
        if amount > purchaseable_amount :
            return Response({'error': 'مبلغ بیشتر از سهم قابل خرید است'}, status=status.HTTP_400_BAD_REQUEST)
        
        if legal_user == True : 
            amount_legal_min = plan.legal_person_minimum_availabe_price #حداقل سهم قابل خرید حقوقی 
            amount_legal_max = plan.legal_person_maximum_availabe_price #حداکثر سهم قابل خرید حقوقی
            
            if amount_legal_min is not None and amount_legal_max is not None :
                if amount < amount_legal_min or amount > amount_legal_max:
                    return Response({'error': 'مبلغ بیشتر یا کمتر از  حد مجاز قرارداد شده است'}, status=status.HTTP_400_BAD_REQUEST)
            else :
                if amount > purchaseable_amount :
                    return Response({'error': 'مبلغ بیشتر از سهم قابل خرید است'}, status=status.HTTP_400_BAD_REQUEST)
                  
                
        if legal_user == False :
            amount_personal_min = plan.real_person_minimum_availabe_price  #حداقل سهم قابل خرید حقیقی
            amount_personal_max = plan.real_person_maximum_available_price #حداکثر سهم قابل خرید حقیقی
            if amount_personal_min is not None and amount_personal_max is not None:
                if amount < amount_personal_min or amount > amount_personal_max :
                    return Response({'error': 'مبلغ بیشتر یا کمتر از  حد مجاز قرارداد شده است'}, status=status.HTTP_400_BAD_REQUEST)
            
            else :
                if amount > purchaseable_amount :
                    return Response({'error': 'مبلغ بیشتر از سهم قابل خرید است'}, status=status.HTTP_400_BAD_REQUEST)
                  


        value = plan.unit_price * amount
        if not request.data.get('payment_id'):
            return Response({'error': 'payment_id not found'}, status=status.HTTP_404_NOT_FOUND)
        payment_id = request.data.get('payment_id')
        description = request.data.get('description',None)
        if not request.data.get('risk_statement'):
            return Response({'error': 'risk_statement not found'}, status=status.HTTP_404_NOT_FOUND)
        payment_id = request.data.get('risk_statement') == 'true'
        if not payment_id:
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
            description = description,
            name_status = name_status,
            picture = picture,
            
        )
        payment.save()
        return Response('success')
    

    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get(self,request,trace_code):
        """
        Retrieve all payment documents for a specific plan.

        This method retrieves payment documents associated with a plan identified by its trace code. 
        If requested by an admin, the complete list is returned; if requested by a user, only completed payments are returned.

        - If the Authorization header is missing, an error is returned.
        - If both the user's and admin's authorization tokens are invalid, an error is returned.
        - If the plan with the specified trace code does not exist, an error is returned.

        Parameters:
            - Authorization (str, header): Authorization token for user or admin.
            - trace_code (str, path): Unique identifier for the plan.

        Responses:
            200: [
                {
                    "amount": <amount>,
                    "value": <total_value>,
                    "create_date": <date>,
                    "fullname": <user_fullname or "نامشخص">,
                    ...
                },
                ...
            ]
            400: {"error": "Authorization header is missing"}
            401: {"error": "Authorization not found"}
            404: {"error": "plan not found"}
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)

        admin = fun.decryptionadmin(Authorization)


        if not admin and not user:
            return Response({'error': 'Authorization not found'}, status=status.HTTP_401_UNAUTHORIZED)
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan:
            return Response({'error': 'plan not found'}, status=status.HTTP_404_NOT_FOUND)

        if admin:
            admin = admin.first()
            payments = PaymentGateway.objects.filter(plan=plan)
            response = serializers.PaymentGatewaySerializer(payments,many=True)
            df = pd.DataFrame(response.data)
            if len(df)==0:
                return Response([], status=status.HTTP_200_OK)
            df['fulname'] = [get_name(x) for x in df['user']]
            df = df.to_dict('records')

            return Response(df, status=status.HTTP_200_OK)
        
        if user:
            user = user.first()
            payments = PaymentGateway.objects.filter(plan=plan , status = '3')
            response = serializers.PaymentGatewaySerializer(payments,many=True)
            df = pd.DataFrame(response.data)
            if len(df)==0:
                return Response([], status=status.HTTP_200_OK)
            df['fullname'] = df.apply(lambda row: get_name(row['user']) if row['name_status'] else 'نامشخص', axis=1)
            df = df[['amount','value','create_date','fullname']]
            df = df.to_dict('records')
            return Response(df, status=status.HTTP_200_OK)

            
    @method_decorator(ratelimit(key='ip', rate='5/m', method='PATCH', block=True))
    def patch (self,request,trace_code) :
        """
        Update a specific payment document status by its ID.

        This method authenticates the admin using the Authorization header and allows them to update the status 
        of a payment document for a plan identified by its trace code. It updates the collected amount based on valid payments.

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - If the plan with the specified trace code does not exist, an error is returned.
        - If the payment document with the specified ID does not exist, an error is returned.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - trace_code (str, path): Unique identifier for the plan.
            - id (int, body): ID of the payment document to update.
            - status (str, body): The updated status of the payment document (optional).

        Responses:
            200: {
                "id": <payment_id>,
                "amount": <amount>,
                "value": <total_value>,
                ...
            }
            400: {"error": "Authorization header is missing"}
            404: {"error": "admin not found" / "plan not found" / "payments not found"}
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
            return Response({'error': 'plan not found'}, status=status.HTTP_404_NOT_FOUND)
        payment_id = request.data.get('id')
        payments = PaymentGateway.objects.filter(plan=plan,id = payment_id).first()
        if not payments :
            return Response({'error': 'payments not found'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data

        serializer = serializers.PaymentGatewaySerializer(payments, data = request.data , partial = True)
        if serializer.is_valid () :
            serializer.save()
        payment = PaymentGateway.objects.filter(plan=plan ,id = payment_id)
        value = 0
        for i in payment : 
            if i.status == '2' or i.status == '3':
               value += i.value
        information = InformationPlan.objects.filter(plan=plan ).first()
        information.amount_collected_now = value
        information.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class PaymentUser(APIView):
    """
    This view allows authenticated users to retrieve their payment documents associated with a specific plan, identified by the plan's trace code.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get(self, request, trace_code):
        """
        Retrieve all payment documents for the authenticated user related to a specific plan.

        This method authenticates the user using the Authorization header and retrieves all payment documents 
        associated with a plan identified by its trace code for the currently authenticated user.

        - If the Authorization header is missing, an error is returned.
        - If the user's authorization token is invalid or the user is not found, an error is returned.
        - If the plan with the specified trace code does not exist, an error is returned.

        Parameters:
            - Authorization (str, header): User's authorization token.
            - trace_code (str, path): Unique identifier for the plan.

        Responses:
            200: [
                {
                    "id": <payment_id>,
                    "plan": <plan_id>,
                    "user": <user_id>,
                    "amount": <amount>,
                    "value": <total_value>,
                    "status": <status>,
                    "payment_id": <payment_id>,
                    "create_date": <create_date>,
                    ...
                },
                ...
            ]
            400: {"error": "Authorization header is missing"}
            401: {"error": "Authorization not found"}
            404: {"error": "plan not found"}
        """
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


class ParticipantViewset(APIView):
    """
    This view allows admins to retrieve a list of participants who have successfully completed payments (status=3) for a specific plan.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get(self, request, trace_code):
        """
        Retrieve all participants for a specific plan with successful payments.

        This method checks the Authorization header to determine if the request is from an admin. If the user is an admin, 
        the participant's names are fully displayed. If not, names are only shown if allowed by the participant's `name_status`.
        
        - If the Authorization header is missing or invalid, access is denied.
        - If the specified plan does not exist, an error is returned.
        - If no participants with a completed payment status (status=3) are found, an error is returned.

        Parameters:
            - Authorization (str, header, optional): Admin's authorization token.
            - trace_code (str, path): Unique identifier for the plan.

        Responses:
            200: [
                {
                    "id": <payment_id>,
                    "plan": <plan_id>,
                    "user": <user_id>,
                    "amount": <amount>,
                    "value": <total_value>,
                    "create_date": <create_date>,
                    "name": <participant_name or "نامشخص">,
                    ...
                },
                ...
            ]
            404: {"error": "admin not found" / "plan not found" / "participant not found"}
        """
        Authorization = request.headers.get('Authorization')
        if  Authorization:
            admin = fun.decryptionadmin(Authorization)
            if not admin:
                return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
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
    """
    This view allows users to request and download a participation certificate in PDF format for a specific plan, 
    identified by the plan's trace code.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request, trace_code):
        """
        Request a participation certificate for a specific plan.

        This method authenticates the user using the Authorization header and generates a participation certificate 
        in PDF format for a specific plan identified by its trace code. The certificate is saved in the media directory, 
        and the URL for the downloaded file is returned.

        - If the Authorization header is missing, an error is returned.
        - If the user's authorization token is invalid or the user is not found, an error is returned.
        - If the specified plan does not exist, an error is returned.
        - If the API request to retrieve the participation report fails, an error with the response from the external API is returned.

        Parameters:
            - Authorization (str, header): User's authorization token.
            - trace_code (str, path): Unique identifier for the plan.

        Responses:
            200: {
                "url": "/media/reports/<trace_code>_<user_uniqueIdentifier>.pdf"
            }
            400: {"error": "Authorization header is missing"}
            401: {"error": "Authorization not found"}
            404: {"error": "plan not found"}
            200 (API Error): <External API error response in JSON format>
        """
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

 
class InformationPlanViewset(APIView):
    """
    This view allows admins to create or update information for a specific plan and retrieve information details 
    for a plan identified by its trace code.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request, trace_code):
        """
        Create or update information for a specific plan.

        This method authenticates the admin using the Authorization header and allows them to create or update 
        information for a plan identified by its trace code. Information includes details like the rate of return, 
        status, visibility, and payment date.

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - If the specified plan does not exist, an error is returned.
        - If the status value is outside the accepted range, it defaults to '1'.
        - The payment date, if provided, should be a Unix timestamp.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - trace_code (str, path): Unique identifier for the plan.
            - rate_of_return (float, body, optional): Rate of return for the plan.
            - status_second (str, body, optional): Secondary status of the plan (default '1').
            - status_show (bool, body, optional): Indicates if the plan status should be publicly visible.
            - payment_date (int, body, optional): Payment date as a Unix timestamp (milliseconds).

        Responses:
            200: {
                "plan": <plan_id>,
                "rate_of_return": <rate_of_return>,
                "status_second": <status_second>,
                "status_show": <status_show>,
                "payment_date": <payment_date>,
                ...
            }
            400: {"error": "Authorization header is missing" / "Invalid plan status"}
            404: {"error": "admin not found"}
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
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
    
    
    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get(self,request,trace_code) : 
        """
        Retrieve information details for a specific plan.

        This method retrieves information details for a plan identified by its trace code. The information includes 
        details like rate of return, status, visibility, and payment date.

        - If the specified plan does not exist, an error is returned.

        Parameters:
            - trace_code (str, path): Unique identifier for the plan.

        Responses:
            200: {
                "plan": <plan_id>,
                "rate_of_return": <rate_of_return>,
                "status_second": <status_second>,
                "status_show": <status_show>,
                "payment_date": <payment_date>,
                ...
            }
            400: {"error": "Invalid plan status"}
        """
        plan = Plan.objects.filter(trace_code=trace_code).first()
        if not plan :
            return Response({'error': 'Invalid plan status'}, status=status.HTTP_400_BAD_REQUEST)
        information = InformationPlan.objects.filter(plan=plan).first()
        serializer = serializers.InformationPlanSerializer(information)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EndOfFundraisingViewset(APIView):
    """
    This view allows admins to create, update, and retrieve end-of-fundraising information for a specific plan, identified by its trace code.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request, trace_code):
        """
        Update existing end-of-fundraising records for a specific plan.

        This method authenticates the admin using the Authorization header and allows them to update end-of-fundraising
        records for a specific plan identified by its trace code. Each item to be updated should include an `id`.

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - If the specified plan or its associated information record does not exist, an error is returned.
        - If any end-of-fundraising item with a specified ID is not found, an error is returned.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - trace_code (str, path): Unique identifier for the plan.
            - data (list, body): List of end-of-fundraising items with fields:
                - id (int): The unique ID of the fundraising record.
                - amount_operator (float, optional): Operator-set amount.
                - date_operator (str, optional): Operator-set date.
                - date_capitalization_operator (str, optional): Operator-set capitalization date.
                - type (int, optional): Type of the fundraising entry.

        Responses:
            200: {
                "date_payement": [...updated end-fundraising items...],
                "date_start": <payment_date>
            }
            400: {"error": "Authorization header is missing" / "ID is required for each fundraising item"}
            404: {"error": "admin not found" / "plan not found" / "information plan not found" / "end of fundraising not found"}
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
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


    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get(self,request,trace_code) : 
        """
        Retrieve end-of-fundraising records for a specific plan.

        This method authenticates the admin using the Authorization header and retrieves end-of-fundraising records 
        associated with a specific plan identified by its trace code. If no records exist, default fundraising 
        records are generated based on plan details.

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - If the specified plan or its associated information record does not exist, an error is returned.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - trace_code (str, path): Unique identifier for the plan.

        Responses:
            200: {
                "date_payments": [...end-fundraising items...],
                "date_start": <payment_date>
            }
            400: {"error": "Authorization header is missing" / "Invalid plan status"}
            404: {"error": "admin not found" / "information plan not found"}
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
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
        

class SendPaymentToFarabours(APIView):
    """
    This view allows admins to send payment information for a financing provider to Farabours.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request, trace_code):
        """
        Send payment details to Farabours.

        This method authenticates the admin using the Authorization header and sends payment details for a specific
        project financing provider to Farabours. It gathers details from the request body and constructs a
        `ProjectFinancingProvider` instance for the payment.

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - Payment details including `projectID`, `nationalID`, and other relevant fields are required in the request body.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - trace_code (str, path): Unique identifier for the project.
            - data (object, body): Payment details with fields:
                - projectID (str): The project identifier.
                - nationalID (str): The financing provider's national ID.
                - isLegal (bool): Indicates if the provider is a legal entity.
                - firstName (str, optional): The first name of the financing provider.
                - lastNameOrCompanyName (str): Last name or company name of the provider.
                - providedFinancePrice (float): The amount of financing provided.
                - bourseCode (str): The provider’s bourse code.
                - paymentDate (str): The payment date.
                - shebaBankAccountNumber (str): The SHEBA bank account number.
                - mobileNumber (str): The provider's mobile number.
                - bankTrackingNumber (str, optional): The bank tracking number for the payment.

        Responses:
            200: { "message": "Payment details sent successfully." }
            400: { "error": "Authorization header is missing" }
            404: { "error": "admin not found" }
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first() 
        data = request.data
        financing_provider = ProjectFinancingProvider(
            projectID=data.get('projectID'),
            nationalID=data.get('nationalID'),
            isLegal=data.get('isLegal'),
            firstName=data.get('firstName'),
            lastNameOrCompanyName=data.get('lastNameOrCompanyName'),
            providedFinancePrice=data.get('providedFinancePrice'),
            bourseCode=data.get('bourseCode'),
            paymentDate=data.get('paymentDate'),
            shebaBankAccountNumber=data.get('shebaBankAccountNumber'),
            mobileNumber=data.get('mobileNumber'),
            bankTrackingNumber=data.get('bankTrackingNumber'),
        )
        return Response (status=status.HTTP_200_OK)


class SendParticipationCertificateToFaraboursViewset(APIView):
    """
    This view sends participation certificate data to Farabours for approved payments.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request, trace_code):
        """
        Send Participation Certificates to Farabours.

        This method validates the admin's authorization and processes approved payments (`status = '3'`)
        for the specified plan. Each payment's information, such as user details, finance price, and bank
        tracking number, is serialized and sent to the Farabours API.

        - If the Authorization header is missing, an error is returned.
        - If the admin's authorization token is invalid or the admin is not found, an error is returned.
        - Only payments with `status = '3'` and `send_farabours = False` are processed.
        - After successfully sending to Farabours, each payment's `send_farabours` status is updated.

        Parameters:
            - Authorization (str, header): Admin's authorization token.
            - trace_code (str, path): Unique identifier for the project.
            - data (object, body): Contains payment details for each project financing provider.

        Responses:
            200: { "message": "Participation certificates sent successfully." }
            400: { "error": "Authorization header is missing" }
            400: { "error": "plan not found" }
            400: { "error": "payment not found" }
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        plan = Plan.objects.filter(trace_code = trace_code).first()
        if not plan :
            return Response({'error': 'plan not found '}, status=status.HTTP_400_BAD_REQUEST)
        payment = PaymentGateway.objects.filter(plan=plan , status = '3' , send_farabours = False)
        if not payment :
            return Response({'error': 'payment not found'}, status=status.HTTP_400_BAD_REQUEST)

        payment_serializer = serializers.PaymentGatewaySerializer(payment , many = True)
        payment_serializer = payment_serializer.data
        api_farabours = CrowdfundingAPI()
        for i in payment_serializer :
            uniqueIdentifier = i['user']
            user_obj = User.objects.filter(uniqueIdentifier=uniqueIdentifier).first()

            if user_obj is not None:
                user_fname = get_fname(uniqueIdentifier)
                user_lname = get_lname(uniqueIdentifier)
                account_number = get_account_number (uniqueIdentifier)
                mobile = get_mobile_number (uniqueIdentifier)
                bourse_code = get_economi_code (uniqueIdentifier)
                is_legal = check_legal_person (uniqueIdentifier)
            provided_finance_price = i['value']
            payment_date = i['create_date']
            bank_tracking_number = i['payment_id']

            project_finance = ProjectFinancingProvider(
                projectID = trace_code,
                nationalID = uniqueIdentifier ,
                isLegal = is_legal,
                firstName = user_fname ,
                lastNameOrCompanyName = user_lname,
                providedFinancePrice = provided_finance_price,
                bourseCode = bourse_code,
                paymentDate = payment_date,
                shebaBankAccountNumber = account_number,
                mobileNumber = mobile,
                bankTrackingNumber = bank_tracking_number,
            )
            # api = api_farabours.register_financing(project_finance)
        for j in payment :
            j.send_farabours = True
            j.save()
            
            
        return Response(True, status=status.HTTP_200_OK)


class WarrantyAdminViewset(APIView):
    """
    This view is used to manage warranties associated with a specific plan. It provides
    endpoints for adding, retrieving, updating, and deleting warranties.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request, *args, **kwargs):
        """
        Add a Warranty to a Plan.

        This endpoint allows an admin to add a new warranty to a specific plan. The warranty
        includes details such as the exporter, date, and type.

        - Authorization is required.
        - The plan must exist for the warranty to be added.

        Parameters:
            - Authorization (str, header): Admin authorization token.
            - key (str, path): Plan trace code.
            - date (int, body, optional): Timestamp of the warranty date.
            - exporter (str, body): Name of the warranty exporter.
            - kind_of_warranty (str, body): Type of warranty.

        Responses:
            200: A list of all warranties associated with the plan.
            400: { "error": "Authorization header is missing" }
            404: { "error": "plan not found" }
        """
        trace_code = kwargs.get('key')
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        plan = Plan.objects.filter(trace_code = trace_code).first()
        if not plan :
            return Response({'error': 'plan not found '}, status=status.HTTP_400_BAD_REQUEST)
        date = request.data.get('date')
        if date:
            try:
                timestamp = int(date) / 1000
                date = datetime.datetime.fromtimestamp(timestamp)
            except (ValueError, TypeError):
                return Response({'error': 'Invalid date format'}, status=400)
        else:
            date = None

       
        warranty = Warranty.objects.create(
            plan = plan,
            exporter = request.data.get('exporter'),
            date = date,
            kind_of_warranty = request.data.get('kind_of_warranty'),
        )
        warranties = Warranty.objects.filter(plan=plan)
        serializer = serializers.WarrantySerializer (warranties , many = True)

        return Response (serializer.data ,  status= status.HTTP_200_OK)
    

    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get (self, request  ,*args, **kwargs) :
        """
        Retrieve Warranties for a Plan.

        This endpoint retrieves all warranties associated with a specific plan. 
        The user must have admin privileges to access this data.

        Parameters:
            - Authorization (str, header): Admin authorization token.
            - key (str, path): Plan trace code.

        Responses:
            200: A list of warranties for the specified plan.
            400: { "error": "Authorization header is missing" }
            404: { "error": "plan not found" }
        """
        trace_code = kwargs.get('key')
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        plan = Plan.objects.filter(trace_code = trace_code).first()
        if not plan :
            return Response({'error': 'plan not found '}, status=status.HTTP_400_BAD_REQUEST)
        warranties = Warranty.objects.filter(plan=plan)
        serializer = serializers.WarrantySerializer (warranties , many = True)
        return Response (serializer.data ,  status= status.HTTP_200_OK)
    
    @method_decorator(ratelimit(key='ip', rate='5/m', method='PATCH', block=True))
    def patch (self,request , *args, **kwargs):
        """
        Update an Existing Warranty.

        This endpoint allows an admin to update an existing warranty's details, such as the date or
        warranty type.

        - The warranty ID is required to locate and update the correct warranty.

        Parameters:
            - Authorization (str, header): Admin authorization token.
            - key (str, path): Plan trace code.
            - id (int, body): ID of the warranty to be updated.
            - date (int, body, optional): New timestamp for the warranty date.

        Responses:
            200: The updated warranty data.
            400: { "error": "warranty ID is required" }
            404: { "error": "warranty not found" }
        """
        trace_code = kwargs.get('key')
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
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
        if data.get('date'):
            try:
                timestamp = int(data['date']) / 1000
                data['date'] = datetime.datetime.fromtimestamp(timestamp)
            except (ValueError, TypeError):
                return Response({'error': 'Invalid date format'}, status=400)

        serializer = serializers.WarrantySerializer(warranties , data= data ,  partial = True )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data ,  status= status.HTTP_200_OK)
        return Response ({'message': 'update is not succsesfuly'} ,  status=status.HTTP_400_BAD_REQUEST  )

    @method_decorator(ratelimit(key='ip', rate='5/m', method='DELETE', block=True))
    def delete (self, request, *args, **kwargs):
        """
        Delete an Existing Warranty.

        This endpoint allows an admin to delete a warranty associated with a specific plan.
        
        - The warranty ID is required to delete the correct warranty.

        Parameters:
            - Authorization (str, header): Admin authorization token.
            - key (str, path): Plan trace code.
            - id (int, body): ID of the warranty to be deleted.

        Responses:
            200: { "message": "Warranty successfully deleted" }
            400: { "error": "warranty ID is required" }
            404: { "error": "warranty not found" }
        """
        trace_code = kwargs.get('key')
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
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


class TransmissionViewset(APIView):
    """
    This view handles purchasing and payment transactions for a specific plan.
    It provides endpoints for initiating a purchase (POST) and confirming a transaction (GET).
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request, *args, **kwargs):
        """
        Initiate a Purchase Transaction.

        This endpoint initiates a transaction for purchasing a specific amount in a plan.
        It checks if the user has the necessary balance and if the purchase meets the minimum and maximum limits.

        - Authorization is required.
        - The user must be authenticated.
        - The purchase amount is validated based on whether the user is a legal entity.

        Parameters:
            - Authorization (str, header): User authorization token.
            - key (str, path): Plan trace code.
            - amount (int, body): Requested purchase amount.
            - name_status (bool, body, optional): Status to determine if the user's name should be displayed.

        Responses:
            200: A URL for completing the purchase transaction.
            400: { "error": "Authorization header is missing" }
            404: { "error": "User not found" }
        """
        trace_code = kwargs.get('key')
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()
        legal_user = check_legal_person(user.uniqueIdentifier)

        plan = Plan.objects.filter(trace_code=trace_code).first()
        information_plan = InformationPlan.objects.filter(plan=plan).first()


        value = request.data.get('amount')  # مبلغ درخواستی کاربر برای خرید 
        amount_collected_now = information_plan.amount_collected_now # مبلغ جمه اوری شده تا به  الان
        plan_total_price = plan.total_units # کل سهم قابل عرضه برای طرح 
        purchaseable_amount = int(plan_total_price - amount_collected_now) # مبلغ قابل خرید همه کاربران 

        if value > purchaseable_amount :
            return Response({'error': 'مبلغ بیشتر از سهم قابل خرید است'}, status=status.HTTP_400_BAD_REQUEST)
        
        if legal_user == True : 
            amount_legal_min = plan.legal_person_minimum_availabe_price #حداقل سهم قابل خرید حقوقی 
            amount_legal_max = plan.legal_person_maximum_availabe_price #حداکثر سهم قابل خرید حقوقی
            
            if amount_legal_min is not None and amount_legal_max is not None :
                if value < amount_legal_min or value > amount_legal_max:
                    return Response({'error': 'مبلغ بیشتر یا کمتر از  حد مجاز قرارداد شده است'}, status=status.HTTP_400_BAD_REQUEST)
            else :
                if value > purchaseable_amount :
                    return Response({'error': 'مبلغ بیشتر از سهم قابل خرید است'}, status=status.HTTP_400_BAD_REQUEST)
                  
                
        else :
            amount_personal_min = plan.real_person_minimum_availabe_price  #حداقل سهم قابل خرید حقیقی
            amount_personal_max = plan.real_person_maximum_available_price #حداکثر سهم قابل خرید حقیقی
            if amount_personal_min is not None and amount_personal_max is not None :
                if value < amount_personal_min or value > amount_personal_max :
                    return Response({'error': 'مبلغ بیشتر یا کمتر از  حد مجاز قرارداد شده است'}, status=status.HTTP_400_BAD_REQUEST)
            
            else :
                if value > purchaseable_amount :
                    return Response({'error': 'مبلغ بیشتر از سهم قابل خرید است'}, status=status.HTTP_400_BAD_REQUEST)
                  

            
        user = User.objects.filter(uniqueIdentifier = user).first()
        full_name = get_name(user.uniqueIdentifier)
        
        pep = PasargadPaymentGateway()
        invoice_data = {
            'invoice' : pep.generator_invoice_number(),
            'invoiceDate': pep.generator_date(),
            'description': 'تست'
            
        }  
        created = pep.create_purchase(
            invoice  = invoice_data['invoice'],
            invoiceDate = invoice_data['invoiceDate'],
            amount = value ,
            callback_url = os.getenv('callback_url'),
            mobile_number = user.mobile,
            service_code =  '8' ,
            payerName = full_name,
            nationalCode = user.uniqueIdentifier,
            description = invoice_data['description'] 
        )
        print(created)
        payment = PaymentGateway.objects.create(
            plan = plan,
            user = user.uniqueIdentifier,
            amount = int(value / plan.unit_price),
            value = value,
            payment_id = invoice_data['invoice'],
            description = invoice_data['description'],
            code = None,
            risk_statement = True,
            status = '2',
            document = False,
            picture = None , 
            send_farabours = True,
            url_id = created['urlId'] , 
            mobile = user.mobile,
            invoice = invoice_data['invoice'],
            name = get_name(user.uniqueIdentifier),
            service_code = '8',
            name_status = request.data.get('name_status')
        )
        payment.save()

        return Response({'url' : created['url'] }, status=status.HTTP_200_OK)
    

    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    @transaction.atomic
    def get (self,request,*args, **kwargs):
        """
        Confirm a Transaction.

        This endpoint confirms a transaction once the payment has been completed.
        It updates the payment status, retrieves all related payment transactions, and saves
        the total collected amount for the plan.

        - Authorization is required.
        - Transaction is updated to reflect a successful payment.

        Parameters:
            - Authorization (str, header): User authorization token.
            - key (str, path): Invoice number for the transaction.

        Responses:
            200: Confirmation of the payment status.
            400: { "error": "Authorization header is missing" }
            404: { "error": "User not found" }
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()
        pep = PasargadPaymentGateway()
        invoice = kwargs.get('key')
        payment = PaymentGateway.objects.filter(invoice = invoice).first()
        if not payment :
            return Response({'error': 'payment not found '}, status=status.HTTP_400_BAD_REQUEST)
        payment.status = True
        payment.save()
        payment_value = PaymentGateway.objects.filter(plan=payment.plan).filter(Q(status='2') | Q(status='3'))
        serializer = serializers.PaymentGatewaySerializer(payment_value , many = True)
        payment_value = pd.DataFrame(serializer.data)
        payment_value = payment_value['value'].sum()
        
        information = InformationPlan.objects.filter(plan=payment.plan).first()
        if not information :
            return Response({'error': 'information plan not found '}, status=status.HTTP_400_BAD_REQUEST)
        information.amount_collected_now = payment_value
        information.save()
        try :
            pep = pep.confirm_transaction(payment.invoice , payment.url_id)
        except :
            return Response({'error':'payment not found '}, status=status.HTTP_400_BAD_REQUEST)
        return Response(True , status=status.HTTP_200_OK)


class BankReceiptViewset(APIView):
    """
    This view provides an endpoint for retrieving bank receipt information for a specific payment.
    The admin user can access the payment details using the payment ID.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get(self, request, id):
        """
        Retrieve Bank Receipt Information.

        This endpoint retrieves the bank receipt details for a specified payment ID.
        Admin authorization is required to access this endpoint.

        - Authorization is required.
        - Only accessible to admin users.

        Parameters:
            - Authorization (str, header): Admin authorization token.
            - id (int, path): Unique ID of the payment record.

        Responses:
            200: Bank receipt information for the specified payment.
            400: { "error": "Authorization header is missing" }
            404: { "error": "admin not found" }
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        admin = fun.decryptionadmin(Authorization)
        if not admin:
            return Response({'error': 'admin not found'}, status=status.HTTP_404_NOT_FOUND)
        admin = admin.first()
        payment = PaymentGateway.objects.filter (id=id)
        serializer = serializers.PaymentGatewaySerializer(payment , many = True)
        
        return Response (serializer.data,status=status.HTTP_200_OK)


class ParticipantMenuViewset(APIView):
    """
    This view provides a menu for participants to access the plans they have invested in.
    Each plan that the authenticated user has participated in will be retrieved and displayed.
    """

    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get(self, request):
        """
        Retrieve Participant's Plans Menu.

        This endpoint retrieves a list of plans in which the authenticated user has invested,
        specifically those marked as having been sent to Farabours.

        - Authorization is required.
        - Accessible by users who have made payments with `send_farabours` set to True.

        Parameters:
            - Authorization (str, header): User authorization token.

        Responses:
            200: List of plans the user has invested in.
            400: { "error": "Authorization header is missing" }
            404: { "error": "User not found" }
        """
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()
        payment = PaymentGateway.objects.filter(user=user, send_farabours =True)
        serializer = serializers.PaymentGatewaySerializer(payment,many = True)
        plans = []
        for i in serializer.data :
            plan = i['plan']
            plan = Plan.objects.filter(id=plan).first()
            if plan:
                if plan not in plans:
                    plans.append(plan) 
        plan_serializer = serializers.PlanSerializer(plans, many=True)
        return Response (plan_serializer.data,status=status.HTTP_200_OK)
    
    

    