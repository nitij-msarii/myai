#!/usr/bin/env python
"""
Test the AI agent with the real grade_sheet1 database
"""
import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myAI.settings')
django.setup()

from AI_agent.views import get_relevant_schema, execute_sql_directly, format_response_for_user, detect_language

def test_real_database():
    """Test the AI agent with real database queries"""
    
    print("🔍 Testing AI Agent with Real Database...")
    print("=" * 80)
    
    # Test schema detection
    print("📊 Getting database schema...")
    schema = get_relevant_schema()
    library_tables = [table for table in schema.keys() if table.startswith('library_')]
    print(f"Found {len(library_tables)} library tables: {library_tables[:5]}...")
    
    # Test queries
    test_queries = [
        # English queries
        "What books are available in the encyclopedia?",
        "Show me all authors",
        "Tell me about Dr. Smith",
        "Is there a book called 'Encyclopedia of Science'?",
        
        # Arabic queries  
        "ما هي الكتب المتوفرة في الموسوعة؟",
        "أريد معلومات عن المؤلفين",
        "هل يوجد كتاب اسمه Encyclopedia of Science؟",
        "من هو Dr. Smith؟"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 60)
        
        language = detect_language(query)
        print(f"🔤 Detected language: {language}")
        
        # Test specific SQL queries based on the query
        if "book" in query.lower() or "كتاب" in query:
            sql = """
            SELECT eb.*, la.name as author_name 
            FROM library_encyclopedia_book eb 
            LEFT JOIN library_authors la ON eb.author_id = la.id 
            LIMIT 3
            """
        elif "author" in query.lower() or "مؤلف" in query:
            sql = "SELECT * FROM library_authors LIMIT 3"
        elif "Dr. Smith" in query or "smith" in query.lower():
            sql = "SELECT * FROM library_authors WHERE name LIKE '%Smith%'"
        elif "Encyclopedia of Science" in query:
            sql = "SELECT eb.*, la.name as author_name FROM library_encyclopedia_book eb LEFT JOIN library_authors la ON eb.author_id = la.id WHERE eb.title LIKE '%Encyclopedia of Science%'"
        else:
            sql = "SELECT eb.*, la.name as author_name FROM library_encyclopedia_book eb LEFT JOIN library_authors la ON eb.author_id = la.id LIMIT 2"
        
        print(f"🗃️  SQL: {sql}")
        
        # Execute SQL
        result = execute_sql_directly(sql)
        print(f"✅ Success: {result['success']}")
        print(f"📈 Count: {result['count']}")
        
        if result['success'] and result['count'] > 0:
            # Format response
            formatted = format_response_for_user(result, language)
            print(f"💬 Response:\n{formatted}")
        else:
            print(f"❌ No results or error: {result.get('error', 'No data')}")
        
        print("-" * 60)
    
    print("\n🎉 Testing completed!")

if __name__ == "__main__":
    test_real_database()
