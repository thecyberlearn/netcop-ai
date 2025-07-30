from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('wallet/', views.wallet, name='wallet'),
    path('workflows/', views.workflows, name='workflows'),
    path('agents/', views.agents_marketplace, name='agents'),
    path('agents/<slug:slug>/', views.agent_detail, name='agent_detail'),
    path('logout/', views.logout_view, name='logout'),
]