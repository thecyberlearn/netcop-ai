from django.urls import path
from . import views

urlpatterns = [
    # Agent execution endpoints
    path('execute/', views.execute_agent, name='execute_agent'),
    path('executions/', views.get_agent_executions, name='agent_executions'),
    path('executions/<uuid:execution_id>/', views.get_execution_detail, name='execution_detail'),
    
    # Agent listing and details
    path('list/', views.list_agents, name='list_agents'),
    path('detail/<slug:slug>/', views.get_agent_detail, name='agent_api_detail'),
]