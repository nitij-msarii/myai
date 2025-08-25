#!/usr/bin/env python
import requests
import json

def test_ai_queries():
    base_url = "http://localhost:8000/AI-agent/ai-query/"
    headers = {"Content-Type": "application/json"}
    
    # Test queries to demonstrate AI agent capabilities
    test_queries = [
        {
            "name": "Show all encyclopedia books",
            "question": "Show me all encyclopedia books with their details and links"
        },
        {
            "name": "Find books by author",
            "question": "Show me all books written by Dr. Smith"
        },
        {
            "name": "Show all users",
            "question": "Display all users in the system"
        },
        {
            "name": "Find courses",
            "question": "Show me all available courses"
        },
        {
            "name": "Search for specific book",
            "question": "Find the Medical Encyclopedia book"
        },
        {
            "name": "Show book details with links",
            "question": "Show me the World History Encyclopedia with all its details and file links"
        }
    ]
    
    print("🤖 AI Agent Query Demonstration")
    print("=" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. {query['name']}")
        print(f"Query: {query['question']}")
        print("-" * 40)
        
        try:
            response = requests.post(
                base_url,
                headers=headers,
                json={"question": query['question']},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Status: Success")
                print(f"Response: {result.get('response', 'No response')}")
                if result.get('executed_sql'):
                    print(f"SQL: {result['executed_sql']}")
                if result.get('result_count'):
                    print(f"Results: {result['result_count']} records")
            else:
                print(f"❌ Status: Error {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print()

if __name__ == "__main__":
    test_ai_queries() 