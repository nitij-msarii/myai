#!/usr/bin/env python
import mysql.connector

def check_database_data():
    try:
        conn = mysql.connector.connect(
            host='localhost', 
            user='root', 
            password='', 
            database='grade_sheet1'
        )
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute('SHOW TABLES')
        tables = cursor.fetchall()
        
        print("Tables with data:")
        tables_with_data = []
        
        for table in tables[:20]:  # Check first 20 tables
            table_name = table[0]
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"✅ {table_name}: {count} rows")
                    tables_with_data.append(table_name)
                else:
                    print(f"❌ {table_name}: 0 rows")
            except Exception as e:
                print(f"❌ {table_name}: Error - {e}")
        
        print(f"\nFound {len(tables_with_data)} tables with data")
        
        # Check some specific tables
        specific_tables = ['library_encyclopedia_book', 'library_books', 'library_authors', 'users', 'newcourse']
        print("\nChecking specific tables:")
        for table in specific_tables:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                print(f"{table}: {count} rows")
            except Exception as e:
                print(f"{table}: Error - {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"Database connection error: {e}")

if __name__ == "__main__":
    check_database_data() 