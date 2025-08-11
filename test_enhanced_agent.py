#!/usr/bin/env python
import os
import sys
import django

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myAI.settings')
django.setup()

from AI_agent.enhanced_agent import EnhancedAIAgent

def test_arabic_queries():
    """Test the enhanced AI agent with Arabic queries"""
    
    agent = EnhancedAIAgent()
    
    # Test queries
    test_queries = [
        "أريد معلومات عن كتاب الروح",
        "من هو ابن قيم الجوزية",
        "أريد كتب الفقه الإسلامي",
        "مقالات عن الفكر الإسلامي",
        "تطبيقات تعليمية",
        "شركات تقنية"
    ]
    
    print("🧪 Testing Enhanced AI Agent with Arabic Queries")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        print("-" * 30)
        
        try:
            response = agent.process_query(query)
            
            if 'error' in response:
                print(f"❌ Error: {response['error']}")
                if 'suggestions' in response:
                    print("💡 Suggestions:")
                    for suggestion in response['suggestions']:
                        print(f"  - {suggestion}")
            else:
                print("✅ Response:")
                if 'title' in response:
                    print(f"  Title: {response['title']}")
                if 'author' in response:
                    print(f"  Author: {response['author']}")
                if 'name' in response:
                    print(f"  Name: {response['name']}")
                
                if 'links' in response:
                    print("🔗 Links:")
                    for link_type, link_url in response['links'].items():
                        if isinstance(link_url, str):
                            print(f"  {link_type}: {link_url}")
                        elif isinstance(link_url, list):
                            print(f"  {link_type}:")
                            for item in link_url:
                                if isinstance(item, dict):
                                    print(f"    - {item.get('title', item.get('name', 'Unknown'))}")
                
                if 'results' in response:
                    print("📊 Results:")
                    for result in response['results']:
                        print(f"  - {result['type']}: {result.get('title', result.get('name', 'Unknown'))}")
                        
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✨ Test completed!")

def test_specific_entities():
    """Test specific entity retrieval"""
    print("\n🎯 Testing Specific Entities")
    print("=" * 30)
    
    agent = EnhancedAIAgent()
    
    # Test book query
    response = agent.process_query("الروح")
    print("Book 'الروح' response:", bool('error' not in response))
    
    # Test author query
    response = agent.process_query("ابن قيم الجوزية")
    print("Author 'ابن قيم الجوزية' response:", bool('error' not in response))
    
    # Test category query
    response = agent.process_query("الفقه الإسلامي")
    print("Category 'الفقه الإسلامي' response:", bool('error' not in response))

if __name__ == "__main__":
    print("🚀 Starting Enhanced AI Agent Tests")
    
    # Check if database is populated
    try:
        from AI_agent.enhanced_models import EnhancedAuthor
        author_count = EnhancedAuthor.objects.count()
        print(f"📊 Found {author_count} authors in database")
        
        if author_count == 0:
            print("⚠️  Database appears empty. Run:")
            print("   python manage.py populate_enhanced_data")
            print("   Then run this test again.")
        else:
            test_arabic_queries()
            test_specific_entities()
            
    except Exception as e:
        print(f"❌ Error checking database: {str(e)}")
        print("💡 Make sure to run migrations first:")
        print("   python manage.py makemigrations")
        print("   python manage.py migrate")
        print("   python manage.py populate_enhanced_data")
