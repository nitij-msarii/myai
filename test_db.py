#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myAI.settings')
django.setup()

from django.db import connections

def test_database():
    try:
        with connections['default'].cursor() as cursor:
            print("✅ Database connection successful!")
            
            # Get all tables
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            print(f"📋 Found {len(tables)} tables:")
            
            for table in tables:
                table_name = table[0]
                print(f"   - {table_name}")
                
                # Get table structure
                try:
                    cursor.execute(f"DESCRIBE {table_name};")
                    columns = cursor.fetchall()
                    print(f"     Columns: {len(columns)}")
                    for col in columns[:3]:  # Show first 3 columns
                        print(f"       {col[0]} ({col[1]})")
                    if len(columns) > 3:
                        print(f"       ... and {len(columns)-3} more columns")
                except Exception as e:
                    print(f"     Error getting structure: {e}")
                print()
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    test_database() 