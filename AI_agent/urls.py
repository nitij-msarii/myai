from django.urls import path
from . import views
from django.shortcuts import render

def test_agent_view(request):
    return render(request, 'test_agent.html')

urlpatterns = [
    # Unified single API endpoint (accept both with and without trailing slash)
    path('query', views.AIQueryView.as_view(), name='ai_query_no_trailing'),
    path('query/', views.AIQueryView.as_view(), name='ai_query'),

    # DB testing
    path('test-db', views.TestDatabaseView.as_view(), name='test_database_no_trailing'),
    path('test-db/', views.TestDatabaseView.as_view(), name='test_database'),

    # Test interface and root
    path('', views.AIInterfaceView(), name='ai_interface'),
    path('test', test_agent_view, name='test_agent_no_trailing'),
    path('test/', test_agent_view, name='test_agent'),
]