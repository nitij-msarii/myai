#!/usr/bin/env python
import os
import sys
import django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myAI.settings')
django.setup()

from AI_agent.views import detect_language, format_response_for_user, execute_sql_directly

# Test a simple Arabic query
query = 'هل يوجد كتاب أولاد حارتنا؟'
print(f'Testing query: {query}')
print(f'Detected language: {detect_language(query)}')

# Test direct SQL execution
sql = "SELECT b.*, a.name as author_name FROM AI_agent_book b JOIN AI_agent_author a ON b.author_id = a.id WHERE b.title LIKE '%أولاد حارتنا%'"
result = execute_sql_directly(sql)
print(f'SQL result success: {result["success"]}')
print(f'SQL result count: {result["count"]}')

if result["success"] and result["count"] > 0:
    print(f'Found book: {result["results"][0]["title"]}')
    print(f'Author: {result["results"][0]["author_name"]}')

# Test response formatting
formatted = format_response_for_user(result, 'arabic')
print(f'Formatted response:\n{formatted}')
