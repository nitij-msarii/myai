#!/usr/bin/env python
"""
Explore the existing grade_sheet1 database structure
"""
import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myAI.settings')
django.setup()

from django.db import connections

def explore_database():
    """Explore the existing database structure and content"""
    
    print("🔍 Exploring grade_sheet1 database...")
    print("=" * 80)
    
    with connections['default'].cursor() as cursor:
        try:
            # Get all tables
            cursor.execute("SHOW TABLES;")
            tables = [row[0] for row in cursor.fetchall()]
            
            print(f"📊 Found {len(tables)} tables:")
            for table in tables:
                print(f"  - {table}")
            
            print("\n" + "=" * 80)
            
            # Analyze each table
            for table in tables:
                print(f"\n📋 Table: {table}")
                print("-" * 60)
                
                try:
                    # Get table structure
                    cursor.execute(f"DESCRIBE {table};")
                    columns = cursor.fetchall()
                    
                    print("🏗️  Structure:")
                    for col in columns:
                        field, type_, null, key, default, extra = col
                        key_info = f" ({key})" if key else ""
                        print(f"   {field}: {type_}{key_info}")
                    
                    # Get row count
                    cursor.execute(f"SELECT COUNT(*) FROM {table};")
                    count = cursor.fetchone()[0]
                    print(f"📈 Row count: {count}")
                    
                    # Get sample data if table has content
                    if count > 0:
                        cursor.execute(f"SELECT * FROM {table} LIMIT 3;")
                        sample_rows = cursor.fetchall()
                        
                        if sample_rows:
                            print("📝 Sample data:")
                            column_names = [desc[0] for desc in cursor.description]
                            
                            for i, row in enumerate(sample_rows, 1):
                                print(f"   Row {i}:")
                                for j, value in enumerate(row):
                                    if value is not None:
                                        # Truncate long values
                                        str_value = str(value)
                                        if len(str_value) > 50:
                                            str_value = str_value[:47] + "..."
                                        print(f"     {column_names[j]}: {str_value}")
                    
                except Exception as e:
                    print(f"❌ Error analyzing table {table}: {e}")
                
                print("-" * 60)
            
            # Look for potential book/library related tables
            print(f"\n🔍 Looking for book/library related tables...")
            book_related = []
            for table in tables:
                table_lower = table.lower()
                if any(keyword in table_lower for keyword in ['book', 'library', 'author', 'encyclopedia', 'article']):
                    book_related.append(table)
            
            if book_related:
                print("📚 Found potential book/library tables:")
                for table in book_related:
                    print(f"  - {table}")
                    
                    # Get detailed info for book-related tables
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table};")
                        count = cursor.fetchone()[0]
                        
                        if count > 0:
                            cursor.execute(f"SELECT * FROM {table} LIMIT 1;")
                            sample = cursor.fetchone()
                            column_names = [desc[0] for desc in cursor.description]
                            
                            print(f"    📊 {count} rows, Sample columns: {', '.join(column_names[:5])}{'...' if len(column_names) > 5 else ''}")
                    except Exception as e:
                        print(f"    ❌ Error: {e}")
            else:
                print("❌ No obvious book/library related tables found")
            
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            print("💡 Make sure MySQL is running and the database 'grade_sheet1' exists")

if __name__ == "__main__":
    explore_database()
