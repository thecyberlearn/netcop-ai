from rest_framework import serializers
from .models import WorkflowUsage


class WorkflowUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowUsage
        fields = ('id', 'workflow_name', 'workflow_url', 'fee_charged', 'status', 'created_at')
        read_only_fields = ('id', 'created_at')


class TriggerWorkflowSerializer(serializers.Serializer):
    data = serializers.JSONField(required=False, default=dict)