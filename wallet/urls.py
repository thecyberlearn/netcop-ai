from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views

urlpatterns = [
    path('top-up/', views.create_checkout_session, name='wallet_topup'),
    path('transactions/', views.transaction_history, name='transaction_history'),
    path('webhook/stripe/', csrf_exempt(views.stripe_webhook), name='stripe_webhook'),
]