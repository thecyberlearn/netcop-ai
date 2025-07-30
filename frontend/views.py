from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from agents.models import Agent, AgentCategory
import json


def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'pages/landing.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'pages/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'pages/register.html')


@login_required(login_url='/login/')
def dashboard(request):
    return render(request, 'pages/dashboard.html')


@login_required(login_url='/login/')
def wallet(request):
    return render(request, 'pages/wallet.html')


@login_required(login_url='/login/')
def workflows(request):
    return render(request, 'pages/workflows.html')


@login_required(login_url='/login/')
def agents_marketplace(request):
    """Dynamic agent marketplace showing all available agents"""
    category_slug = request.GET.get('category')
    search_query = request.GET.get('search', '').strip()
    
    # Get all active agents
    agents = Agent.objects.filter(is_active=True)
    
    # Filter by category if specified
    if category_slug:
        agents = agents.filter(category__slug=category_slug)
    
    # Filter by search query if specified
    if search_query:
        agents = agents.filter(
            name__icontains=search_query
        ) | agents.filter(
            short_description__icontains=search_query
        ) | agents.filter(
            description__icontains=search_query
        )
    
    # Get all categories for filter menu
    categories = AgentCategory.objects.filter(is_active=True)
    
    context = {
        'agents': agents,
        'categories': categories,
        'current_category': category_slug,
        'search_query': search_query,
    }
    return render(request, 'pages/agents.html', context)


@login_required(login_url='/login/')
def agent_detail(request, slug):
    """Dynamic agent detail page with form rendering"""
    agent = get_object_or_404(Agent, slug=slug, is_active=True)
    
    context = {
        'agent': agent,
        'agent_form_schema_json': json.dumps(agent.form_schema),
        'user_wallet_balance': float(request.user.wallet_balance),
    }
    return render(request, 'pages/agent_detail.html', context)


def logout_view(request):
    return redirect('/')
