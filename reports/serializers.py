from rest_framework import serializers
from . import models
from plan.serializers import PlanSerializer
from plan.models import Plan


class AuditReportSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    class Meta:
        model = models.AuditReport
        fields = '__all__'



class ProgressReportSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    class Meta:
        model = models.ProgressReport
        fields = '__all__'

