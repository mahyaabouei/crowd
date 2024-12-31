from rest_framework import serializers
from . import models
from authentication.models import User , privatePerson , Admin


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Plan
        fields = '__all__'


class ListOfProjectBoardMembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ListOfProjectBoardMembers
        fields = '__all__'


class ProjectOwnerCompansSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProjectOwnerCompan
        fields = '__all__'


class ListOfProjectBigShareHoldersSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ListOfProjectBigShareHolders
        fields = '__all__'

class PicturePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PicturePlan
        fields = '__all__'


class InformationPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.InformationPlan
        fields = '__all__'


class EndOfFundraisingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EndOfFundraising
        fields = '__all__'


class WarrantySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Warranty
        fields = '__all__'



class DocumentationSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(many=True, read_only=True, source='plan_set')
    class Meta:
        model = models.DocumentationFiles
        fields = '__all__'



class AppendicesSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(many=True, read_only=True, source='plan_set')
    class Meta:
        model = models.Appendices
        fields = '__all__'


class CommenttSerializer(serializers.ModelSerializer):
    firstName = serializers.SerializerMethodField()  
    lastName = serializers.SerializerMethodField() 

    class Meta:
        model = models.Comment
        fields = ['id', 'comment', 'status', 'known', 'firstName', 'lastName' , 'answer']

    def get_firstName(self, obj):
        private_person = privatePerson.objects.filter(user=obj.user).first()
        if private_person:
            return private_person.firstName
        return None

    def get_lastName(self, obj):
        private_person = privatePerson.objects.filter(user=obj.user).first()
        if private_person:
            return private_person.lastName
        return None



class PlansSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Plans
        fields = '__all__'
class PaymentGatewaySerializer(serializers.ModelSerializer):
    admin = serializers.PrimaryKeyRelatedField(queryset=Admin.objects.all())
    admin_info = serializers.SerializerMethodField()  
    class Meta:
        model = models.PaymentGateway
        fields = '__all__'
    

    def get_admin_info(self, obj):
        if obj.admin:
            admin = obj.admin
            return {
            'id': admin.id,
            'first_name': admin.firstName or "",
            'last_name': admin.lastName or "",
            'mobile': admin.mobile or "",
            'uniqueIdentifier': admin.uniqueIdentifier or "",
            'email': admin.email or "",
        }
        return {}

class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Complaint
        fields = '__all__'

