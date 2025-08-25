#!/usr/bin/env python
"""
Test the API using requests library (like curl)
"""
import requests
import json

def test_api_with_requests():
    """Test the API using requests library"""
    
    print("🌐 Testing AI Agent API with HTTP Requests")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8002"
    
    test_queries = [
        {
            "question": "Is the book 'Encyclopedia of Science' available?",
            "description": "English book availability check"
        },
        {
            "question": "هل يوجد كتاب موسوعة العلوم؟",
            "description": "Arabic book availability check"
        },
        {
            "question": "What books are available?",
            "description": "General book listing"
        },
        {
            "question": "Tell me about Dr. Smith",
            "description": "Author information"
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        question = test_case["question"]
        description = test_case["description"]
        
        print(f"\n📝 Test {i}: {description}")
        print(f"Query: {question}")
        print("-" * 50)
        
        try:
            # Test with form data
            print("🔄 Testing with form data...")
            response = requests.post(
                f"{base_url}/ai/query/",
                data={'question': question},
                timeout=30
            )
            
            print(f"✅ Status Code: {response.status_code}")
            print(f"📄 Content Type: {response.headers.get('content-type', 'unknown')}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    
                    print(f"🔤 Language: {result.get('language', 'unknown')}")
                    print(f"📊 Success: {result.get('success', False)}")
                    print(f"📈 Results: {result.get('result_count', 0)}")
                    
                    if result.get('executed_sql'):
                        sql = result['executed_sql']
                        print(f"🗃️  SQL: {sql[:80]}...")
                    
                    response_text = result.get('response', 'No response')
                    if len(response_text) > 300:
                        response_text = response_text[:300] + "..."
                    print(f"💬 Response:\n{response_text}")
                    
                except json.JSONDecodeError:
                    print(f"📄 Raw Response: {response.text[:300]}...")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Server not running")
            print("💡 Start server with: python manage.py runserver 127.0.0.1:8002")
            return False
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        print("-" * 50)
    
    return True

def test_server_status():
    """Test if server is running"""
    try:
        response = requests.get("http://127.0.0.1:8002/", timeout=5)
        print(f"✅ Server is running (Status: {response.status_code})")
        return True
    except:
        print("❌ Server is not running")
        return False

if __name__ == "__main__":
    print("🔍 Checking server status...")
    if test_server_status():
        test_api_with_requests()
    else:
        print("💡 Start server with: python manage.py runserver 127.0.0.1:8002")
