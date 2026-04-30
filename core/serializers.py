from rest_framework import serializers
from .models import Workflow, Step, Execution, RiskAssessment

class WorkFlowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Workflow
        fields = '__all__'
        read_only_fields = ['owner', 'created_at']

class StepSerializer(serializers.ModelSerializer):

    class Meta:
        model = Step
        fields = '__all__'
        read_only_fields = ['workflow']

class ExecutionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Execution
        fields = '__all__'

class RiskAssessmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = RiskAssessment
        fields = '__all__'
