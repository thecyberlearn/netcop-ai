import uuid
import json
import requests
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import Agent, AgentExecution
from users.models import User


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def execute_agent(request):
    """Execute an agent with user input data"""
    try:
        # Get request data
        agent_slug = request.data.get('agent_slug')
        input_data = request.data.get('input_data', {})
        
        if not agent_slug:
            return Response(
                {'error': 'agent_slug is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the agent
        agent = get_object_or_404(Agent, slug=agent_slug, is_active=True)
        
        # Check user wallet balance
        user = request.user
        if user.wallet_balance < agent.price:
            return Response(
                {'error': f'Insufficient balance. You need {agent.price} AED but have {user.wallet_balance} AED. Please top up your wallet.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create agent execution record
        execution = AgentExecution.objects.create(
            user=user,
            agent=agent,
            input_data=input_data,
            price_paid=agent.price,
            status='processing'
        )
        
        # Deduct amount from wallet
        user.deduct_balance(agent.price)
        
        # Generate session ID for n8n
        session_id = f"session_{int(timezone.now().timestamp() * 1000)}_{execution.id.hex[:8]}"
        
        # Format input data as message text
        message_text = format_input_data_as_text(input_data, agent)
        
        # Prepare webhook payload matching n8n format
        webhook_payload = {
            "sessionId": session_id,
            "message": {
                "text": message_text
            },
            "webhookUrl": agent.n8n_webhook_url,
            "executionMode": "production",
            "agentId": str(agent.id),
            "executionId": str(execution.id),
            "userId": str(user.id)
        }
        
        try:
            # Send request to n8n webhook
            response = requests.post(
                agent.n8n_webhook_url,
                json=webhook_payload,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'NetCop-AI-Agent/1.0'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                # Parse n8n response
                try:
                    response_data = response.json()
                except:
                    response_data = {"raw_response": response.text}
                
                # Update execution with success
                execution.output_data = response_data
                execution.status = 'success'
                execution.completed_at = timezone.now()
                execution.save()
                
                # Increment agent usage count
                agent.increment_usage()
                
                return Response({
                    'status': 'success',
                    'execution_id': str(execution.id),
                    'output_data': response_data,
                    'price_paid': float(agent.price),
                    'remaining_balance': float(user.wallet_balance)
                })
            else:
                # Handle n8n error with user-friendly message
                try:
                    error_data = response.json()
                    if response.status_code == 404:
                        user_error = f"This AI agent is temporarily unavailable. Please try again later or contact support."
                    elif 'webhook' in error_data.get('message', '').lower():
                        user_error = f"AI service is currently offline. Please try again in a few minutes."
                    else:
                        user_error = f"AI processing failed. Please try again or contact support."
                except:
                    user_error = f"AI service is currently unavailable. Please try again later."
                
                # Log technical details for debugging
                technical_error = f"n8n webhook failed with status {response.status_code}: {response.text}"
                print(f"Agent execution error: {technical_error}")
                
                # Update execution with technical error for admin
                execution.status = 'failed'
                execution.error_message = technical_error
                execution.completed_at = timezone.now()
                execution.save()
                
                # Refund user wallet
                user.add_balance(agent.price)
                
                return Response(
                    {'error': user_error}, 
                    status=status.HTTP_502_BAD_GATEWAY
                )
                
        except requests.exceptions.Timeout:
            user_error = "AI processing is taking longer than expected. Please try again."
            technical_error = "n8n webhook request timed out"
            
            print(f"Agent execution timeout: {technical_error}")
            
            execution.status = 'failed'
            execution.error_message = technical_error
            execution.completed_at = timezone.now()
            execution.save()
            
            # Refund user wallet
            user.add_balance(agent.price)
            
            return Response(
                {'error': user_error}, 
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
            
        except requests.exceptions.RequestException as e:
            user_error = "Unable to connect to AI service. Please check your internet connection and try again."
            technical_error = f"Failed to connect to n8n webhook: {str(e)}"
            
            print(f"Agent execution connection error: {technical_error}")
            
            execution.status = 'failed'  
            execution.error_message = technical_error
            execution.completed_at = timezone.now()
            execution.save()
            
            # Refund user wallet
            user.add_balance(agent.price)
            
            return Response(
                {'error': user_error}, 
                status=status.HTTP_502_BAD_GATEWAY
            )
        
    except Exception as e:
        return Response(
            {'error': f'Internal server error: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def format_input_data_as_text(input_data, agent):
    """Format user input data as a natural text message for n8n"""
    
    # Try to create a natural language description
    if not input_data:
        return f"Execute {agent.name} with default parameters."
    
    # Get form schema for context
    form_schema = agent.form_schema
    field_labels = {}
    
    if form_schema and 'fields' in form_schema:
        for field in form_schema['fields']:
            field_labels[field['name']] = field.get('label', field['name'])
    
    # Build natural text from input data
    text_parts = [f"Execute {agent.name} with the following parameters:"]
    
    for key, value in input_data.items():
        if value:  # Only include non-empty values
            label = field_labels.get(key, key.replace('_', ' ').title())
            text_parts.append(f"{label}: {value}")
    
    return ". ".join(text_parts) + "."


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_agent_executions(request):
    """Get user's agent execution history"""
    try:
        executions = AgentExecution.objects.filter(
            user=request.user
        ).select_related('agent').order_by('-created_at')
        
        # Pagination
        page_size = 20
        page = int(request.GET.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size
        
        executions_data = []
        for execution in executions[start:end]:
            executions_data.append({
                'id': str(execution.id),
                'agent_name': execution.agent.name,
                'agent_slug': execution.agent.slug,
                'status': execution.status,
                'price_paid': float(execution.price_paid),  
                'created_at': execution.created_at.isoformat(),
                'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
                'has_output': bool(execution.output_data),
                'error_message': execution.error_message
            })
        
        return Response({
            'executions': executions_data,
            'page': page,
            'has_next': len(executions) > end,
            'total_count': executions.count()
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch executions: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_execution_detail(request, execution_id):
    """Get detailed information about a specific execution"""
    try:
        execution = get_object_or_404(
            AgentExecution, 
            id=execution_id, 
            user=request.user
        )
        
        return Response({
            'id': str(execution.id),
            'agent': {
                'name': execution.agent.name,
                'slug': execution.agent.slug,
                'description': execution.agent.description
            },
            'status': execution.status,
            'price_paid': float(execution.price_paid),
            'input_data': execution.input_data,
            'output_data': execution.output_data,
            'error_message': execution.error_message,
            'created_at': execution.created_at.isoformat(),
            'updated_at': execution.updated_at.isoformat(),
            'completed_at': execution.completed_at.isoformat() if execution.completed_at else None
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch execution details: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_agents(request):
    """List all available agents with filtering"""
    try:
        agents = Agent.objects.filter(is_active=True)
        
        # Filter by category
        category_slug = request.GET.get('category')
        if category_slug:
            agents = agents.filter(category__slug=category_slug)
        
        # Search
        search = request.GET.get('search', '').strip()
        if search:
            agents = agents.filter(
                name__icontains=search
            ) | agents.filter(
                short_description__icontains=search
            )
        
        agents_data = []
        for agent in agents:
            agents_data.append({
                'id': str(agent.id),
                'name': agent.name,
                'slug': agent.slug,
                'short_description': agent.short_description,
                'price': float(agent.price),
                'category': {
                    'name': agent.category.name,  
                    'slug': agent.category.slug
                },
                'usage_count': agent.usage_count,
                'is_featured': agent.is_featured,
                'icon': agent.icon
            })
        
        return Response({'agents': agents_data})
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch agents: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_agent_detail(request, slug):
    """Get detailed information about a specific agent"""
    try:
        agent = get_object_or_404(Agent, slug=slug, is_active=True)
        
        return Response({
            'id': str(agent.id),
            'name': agent.name,
            'slug': agent.slug,
            'description': agent.description,
            'short_description': agent.short_description,
            'price': float(agent.price),
            'category': {
                'name': agent.category.name,
                'slug': agent.category.slug
            },
            'form_schema': agent.form_schema,
            'usage_count': agent.usage_count,
            'is_featured': agent.is_featured,
            'icon': agent.icon,
            'created_at': agent.created_at.isoformat()
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch agent details: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
