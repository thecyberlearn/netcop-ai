import stripe
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from decimal import Decimal
from .models import WalletTransaction
from .serializers import WalletTransactionSerializer, TopUpSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY


@api_view(['POST'])
def create_checkout_session(request):
    serializer = TopUpSerializer(data=request.data)
    if serializer.is_valid():
        amount = serializer.validated_data['amount']
        
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Wallet Top-up',
                        },
                        'unit_amount': int(amount * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/success/'),
                cancel_url=request.build_absolute_uri('/cancel/'),
                metadata={
                    'user_id': str(request.user.id),
                    'amount': str(amount),
                }
            )
            
            WalletTransaction.objects.create(
                user=request.user,
                transaction_type='deposit',
                amount=amount,
                status='pending',
                stripe_payment_intent_id=checkout_session.payment_intent,
                description=f'Wallet top-up via Stripe'
            )
            
            return Response({
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def transaction_history(request):
    transactions = WalletTransaction.objects.filter(user=request.user)
    serializer = WalletTransactionSerializer(transactions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return Response({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return Response({'error': 'Invalid signature'}, status=400)
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata']['user_id']
        amount = Decimal(session['metadata']['amount'])
        
        try:
            from users.models import User
            user = User.objects.get(id=user_id)
            
            transaction = WalletTransaction.objects.get(
                stripe_payment_intent_id=session['payment_intent'],
                user=user,
                status='pending'
            )
            
            transaction.status = 'completed'
            transaction.save()
            
            user.add_balance(amount)
            
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=400)
        except WalletTransaction.DoesNotExist:
            return Response({'error': 'Transaction not found'}, status=400)
    
    return Response({'status': 'success'})
