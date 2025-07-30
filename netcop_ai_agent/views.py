from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        'message': 'NetCop AI Agent API',
        'version': '1.0',
        'endpoints': {
            'authentication': {
                'register': '/api/auth/register/',
                'login': '/api/auth/login/',
                'profile': '/api/auth/profile/',
            },
            'wallet': {
                'top_up': '/api/wallet/top-up/',
                'transactions': '/api/wallet/transactions/',
                'stripe_webhook': '/api/wallet/webhook/stripe/',
            },
            'workflows': {
                'trigger': '/api/workflows/trigger/<workflow_name>/',
                'history': '/api/workflows/history/',
            },
            'admin': '/admin/',
        },
        'documentation': {
            'auth_required': 'Most endpoints require Authorization: Token <your-token>',
            'workflow_fee': '$0.10 per workflow execution',
            'rate_limit': '10 requests per minute for workflows'
        }
    })