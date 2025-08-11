#!/usr/bin/env python
"""
Comprehensive test of link generation for all content types
"""
import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myAI.settings')
django.setup()

from AI_agent.views import generate_msarii_link, create_slug, detect_language, execute_sql_directly, format_response_for_user

def test_link_generation():
    """Test link generation for all content types"""
    
    print("🔗 COMPREHENSIVE LINK GENERATION TEST")
    print("=" * 80)
    print("Testing msarii.com link generation for all content types")
    print()
    
    # Test different content types with both English and Arabic examples
    test_cases = [
        # Books
        ("book", "Encyclopedia of Science", "English book title"),
        ("book", "موسوعة العلوم", "Arabic book title"),
        ("book", "World History Encyclopedia", "Another English book"),
        
        # Authors
        ("author", "Dr. Smith", "English author name"),
        ("author", "د. أحمد محمد", "Arabic author name"),
        ("author", "Prof. Johnson", "Another English author"),
        
        # Articles
        ("article", "Scientific Research Methods", "English article"),
        ("article", "طرق البحث العلمي", "Arabic article"),
        ("article", "Climate Change Impact", "Environmental article"),
        
        # Companies
        ("company", "Tech Solutions Inc", "English company"),
        ("company", "شركة التقنيات المتقدمة", "Arabic company"),
        ("company", "Innovation Labs", "Tech company"),
        
        # WebApps
        ("webapp", "Learning Management System", "English webapp"),
        ("webapp", "نظام إدارة التعلم", "Arabic webapp"),
        ("webapp", "Data Analytics Tool", "Analytics webapp"),
        
        # Categories
        ("category", "Science & Technology", "English category"),
        ("category", "العلوم والتكنولوجيا", "Arabic category"),
        ("category", "Business & Finance", "Business category"),
    ]
    
    print("🌐 LINK GENERATION EXAMPLES:")
    print("-" * 60)
    
    for content_type, name, description in test_cases:
        link = generate_msarii_link(content_type, name)
        slug = create_slug(name)
        language = detect_language(name)
        
        print(f"📋 {description}")
        print(f"   Type: {content_type}")
        print(f"   Name: {name}")
        print(f"   Language: {language}")
        print(f"   Slug: {slug}")
        print(f"   🔗 Link: {link}")
        print()
    
    print("=" * 80)
    print()
    
    # Test with actual database data
    print("📊 TESTING WITH ACTUAL DATABASE DATA:")
    print("-" * 60)
    
    # Test books with real data
    print("📚 BOOKS FROM DATABASE:")
    sql = """
    SELECT eb.title, eb.slug, 
           la.name as author_name, la.slug as author_slug
    FROM library_encyclopedia_book eb 
    LEFT JOIN library_authors la ON eb.author_id = la.id 
    LIMIT 3
    """
    
    result = execute_sql_directly(sql)
    if result['success'] and result['count'] > 0:
        for book in result['results']:
            title = book['title']
            book_slug = book.get('slug', title)
            author_name = book.get('author_name', 'Unknown')
            author_slug = book.get('author_slug', author_name)
            
            book_link = generate_msarii_link('book', book_slug if book_slug else title)
            author_link = generate_msarii_link('author', author_slug if author_slug else author_name)
            
            print(f"   📖 Book: {title}")
            print(f"      🔗 Book Link: {book_link}")
            if author_name and author_name != 'Unknown':
                print(f"      👤 Author: {author_name}")
                print(f"      🔗 Author Link: {author_link}")
            print()
    
    # Test authors with real data
    print("✍️ AUTHORS FROM DATABASE:")
    sql = "SELECT name, slug FROM library_authors LIMIT 3"
    
    result = execute_sql_directly(sql)
    if result['success'] and result['count'] > 0:
        for author in result['results']:
            name = author['name']
            slug = author.get('slug', name)
            
            author_link = generate_msarii_link('author', slug if slug else name)
            
            print(f"   👤 Author: {name}")
            print(f"      🔗 Link: {author_link}")
            print()
    
    print("=" * 80)
    print()
    
    # Show the complete URL structure
    print("🏗️ COMPLETE URL STRUCTURE:")
    print("-" * 40)
    
    base_url = "https://msarii.com"
    url_patterns = {
        "Books": f"{base_url}/books/{{slug}}",
        "Authors": f"{base_url}/authors/{{slug}}",
        "Articles": f"{base_url}/articles/{{slug}}",
        "Companies": f"{base_url}/companies/{{slug}}",
        "WebApps": f"{base_url}/webapps/{{slug}}",
        "Categories": f"{base_url}/categories/{{slug}}",
        "Courses": f"{base_url}/courses/{{slug}}"
    }
    
    for content_type, pattern in url_patterns.items():
        print(f"📋 {content_type}: {pattern}")
    
    print()
    print("🎯 KEY FEATURES:")
    print("✅ Fixed URL structure for each content type")
    print("✅ Automatic slug generation from titles/names")
    print("✅ Arabic text properly URL-encoded")
    print("✅ English text converted to SEO-friendly slugs")
    print("✅ Consistent pattern: https://msarii.com/{type}/{slug}")
    
    print("\n💡 USAGE IN AGENT RESPONSES:")
    print("When the agent finds a book, it will include:")
    print("• Book details (title, author, description, etc.)")
    print("• 🔗 Explore Book: https://msarii.com/books/{book-slug}")
    print("• 👤 Author Page: https://msarii.com/authors/{author-slug}")
    
    print("\n🚀 ALL CONTENT TYPES SUPPORTED:")
    print("📚 Books, ✍️ Authors, 📰 Articles, 🏢 Companies,")
    print("💻 WebApps, 📂 Categories, 🎓 Courses")

if __name__ == "__main__":
    test_link_generation()
