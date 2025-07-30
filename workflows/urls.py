from django.urls import path
from . import views

urlpatterns = [
    path('trigger/<str:workflow_name>/', views.trigger_workflow, name='trigger_workflow'),
    path('history/', views.workflow_history, name='workflow_history'),
]