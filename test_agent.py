#!/usr/bin/env python
"""
Test script for the improved AI agent with Arabic support
"""
import os
import sys
import django
import json

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myAI.settings')
django.setup()

from AI_agent.views import AIQueryView
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request

def test_agent_queries():
    """Test the AI agent with various Arabic and English queries"""
    
    factory = APIRequestFactory()
    view = AIQueryView()
    
    # Test queries in both Arabic and English
    test_queries = [
        # Arabic queries
        "هل يوجد كتاب أولاد حارتنا في قاعدة البيانات؟",
        "من هو نجيب محفوظ؟",
        "ما هي الكتب المتوفرة؟",
        "أريد معلومات عن المؤلفين",
        
        # English queries  
        "Is the book 'أولاد حارتنا' available in the database?",
        "Who is نجيب محفوظ?",
        "What books are available?",
        "Tell me about the authors",
        "Show me all books by طه حسين"
    ]
    
    print("🤖 Testing AI Agent with Arabic and English queries...\n")
    print("=" * 80)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 60)
        
        # Create request
        request = factory.post('/ai/query/', {'question': query}, format='json')
        django_request = Request(request)
        
        try:
            # Call the view
            response = view.post(django_request)
            result = response.data
            
            print(f"✅ Status: {response.status_code}")
            print(f"🔤 Language: {result.get('language', 'unknown')}")
            print(f"📊 Success: {result.get('success', False)}")
            print(f"📈 Result Count: {result.get('result_count', 0)}")
            
            if result.get('executed_sql'):
                print(f"🗃️  SQL: {result['executed_sql']}")
            
            print(f"💬 Response:\n{result.get('response', 'No response')}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 60)
    
    print("\n🎉 Testing completed!")

if __name__ == "__main__":
    test_agent_queries()
