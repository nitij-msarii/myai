from django.urls import path
from . import views
from django.shortcuts import render

def test_agent_view(request):
    return render(request, 'test_agent.html')

urlpatterns = [
    path('query/', views.simple_ai_query, name='simple_query'),  # Simple Django view
    path('query-drf/', views.SimpleQueryView.as_view(), name='simple_query_drf'),  # DRF view
    path('query-full/', views.AIQueryView.as_view(), name='ai_query'),  # Full AutoGen view
    path('test-db/', views.TestDatabaseView.as_view(), name='test_database'),
    path('', views.AIInterfaceView(), name='ai_interface'),
    path('test/', test_agent_view, name='test_agent'),
]