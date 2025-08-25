from django.urls import path
from . import views

urlpatterns = [
    path('query/', views.AIQueryView.as_view(), name='ai_query'),
    path('test-database/', views.TestDatabaseView.as_view(), name='test_database'),
    path('simple-query/', views.simple_ai_query, name='simple_ai_query'),
]