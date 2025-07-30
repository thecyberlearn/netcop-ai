import requests
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from decimal import Decimal
from django.db import transaction
from django_ratelimit.decorators import ratelimit
from .models import WorkflowUsage
from .serializers import WorkflowUsageSerializer, TriggerWorkflowSerializer
from wallet.models import WalletTransaction


@api_view(['POST'])
@ratelimit(key='user', rate='10/m', method='POST', block=True)
def trigger_workflow(request, workflow_name):
    serializer = TriggerWorkflowSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    workflow_data = serializer.validated_data.get('data', {})
    workflow_fee = Decimal(str(settings.WORKFLOW_FEE))
    
    if not request.user.has_sufficient_balance(workflow_fee):
        return Response({
            'error': 'Insufficient wallet balance',
            'required': str(workflow_fee),
            'current_balance': str(request.user.wallet_balance)
        }, status=status.HTTP_402_PAYMENT_REQUIRED)
    
    workflow_url = f"{settings.N8N_WEBHOOK_URL.rstrip('/')}/{workflow_name}"
    
    with transaction.atomic():
        workflow_usage = WorkflowUsage.objects.create(
            user=request.user,
            workflow_name=workflow_name,
            workflow_url=workflow_url,
            fee_charged=workflow_fee,
            request_data=workflow_data,
            status='pending'
        )
        
        if not request.user.deduct_balance(workflow_fee):
            return Response({
                'error': 'Failed to deduct balance'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        WalletTransaction.objects.create(
            user=request.user,
            transaction_type='fee',
            amount=workflow_fee,
            status='completed',
            description=f'Workflow fee for {workflow_name}'
        )
        
        try:
            headers = {}
            if settings.N8N_API_KEY:
                headers['Authorization'] = f'Bearer {settings.N8N_API_KEY}'
            
            response = requests.post(
                workflow_url,
                json=workflow_data,
                headers=headers,
                timeout=30
            )
            
            workflow_usage.response_data = response.json() if response.content else {}
            workflow_usage.status = 'success' if response.status_code == 200 else 'failed'
            
            if response.status_code != 200:
                workflow_usage.error_message = f"HTTP {response.status_code}: {response.text}"
            
            workflow_usage.save()
            
            return Response({
                'success': workflow_usage.status == 'success',
                'workflow_usage_id': workflow_usage.id,
                'fee_charged': workflow_fee,
                'response_data': workflow_usage.response_data,
                'remaining_balance': request.user.wallet_balance
            })
            
        except requests.RequestException as e:
            workflow_usage.status = 'failed'
            workflow_usage.error_message = str(e)
            workflow_usage.save()
            
            return Response({
                'success': False,
                'workflow_usage_id': workflow_usage.id,
                'error': str(e),
                'fee_charged': workflow_fee,
                'remaining_balance': request.user.wallet_balance
            })


@api_view(['GET'])
def workflow_history(request):
    usage_history = WorkflowUsage.objects.filter(user=request.user)
    serializer = WorkflowUsageSerializer(usage_history, many=True)
    return Response(serializer.data)
