from rest_framework import serializers
from . import models
from plan.serializers import PlanSerializer

class AuditReportSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(many=True, read_only=True, source='plan_set')
    class Meta:
        model = models.AuditReport
        fields = '__all__'



class ProgressReportSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(many=True, read_only=True, source='plan_set')
    class Meta:
        model = models.ProgressReport
        fields = '__all__'

