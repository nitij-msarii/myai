#!/usr/bin/env python
"""
Simple test of link generation without importing autogen
"""
import re
import urllib.parse

def detect_language(text):
    """Detect if text is primarily Arabic or English"""
    arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
    total_chars = len([char for char in text if char.isalpha()])
    if total_chars == 0:
        return "english"
    arabic_ratio = arabic_chars / total_chars
    return "arabic" if arabic_ratio > 0.3 else "english"

def create_slug(text):
    """Create URL-friendly slug from Arabic or English text"""
    if not text:
        return ""
    # For Arabic text, we'll use the text as-is but URL encode it
    # For English text, we'll create a standard slug
    text = str(text).strip()
    if detect_language(text) == "arabic":
        return urllib.parse.quote(text, safe='')
    else:
        # Standard English slug creation
        text = re.sub(r'[^\w\s-]', '', text.lower())
        return re.sub(r'[-\s]+', '-', text).strip('-')

def generate_msarii_link(item_type, name_or_title):
    """Generate msarii.com links based on item type and name/title"""
    base_url = "https://msarii.com"
    slug = create_slug(name_or_title)
    
    link_mapping = {
        'author': f"{base_url}/authors/{slug}",
        'book': f"{base_url}/books/{slug}",
        'course': f"{base_url}/courses/{slug}",
        'article': f"{base_url}/articles/{slug}",
        'category': f"{base_url}/categories/{slug}",
        'company': f"{base_url}/companies/{slug}",
        'webapp': f"{base_url}/webapps/{slug}"
    }
    
    return link_mapping.get(item_type, f"{base_url}/{slug}")

def test_link_generation():
    """Test link generation for all content types"""
    
    print("🔗 COMPREHENSIVE LINK GENERATION DEMONSTRATION")
    print("=" * 80)
    print("Testing msarii.com link generation for all content types")
    print()
    
    # Test different content types with both English and Arabic examples
    test_cases = [
        # Books
        ("book", "Encyclopedia of Science", "English book title"),
        ("book", "موسوعة العلوم", "Arabic book title"),
        ("book", "World History Encyclopedia", "Another English book"),
        ("book", "كتاب التاريخ الإسلامي", "Arabic history book"),
        
        # Authors
        ("author", "Dr. Smith", "English author name"),
        ("author", "د. أحمد محمد", "Arabic author name"),
        ("author", "Prof. Johnson", "Another English author"),
        ("author", "الدكتور محمد علي", "Arabic doctor name"),
        
        # Articles
        ("article", "Scientific Research Methods", "English article"),
        ("article", "طرق البحث العلمي", "Arabic article"),
        ("article", "Climate Change Impact", "Environmental article"),
        ("article", "تأثير التغير المناخي", "Arabic climate article"),
        
        # Companies
        ("company", "Tech Solutions Inc", "English company"),
        ("company", "شركة التقنيات المتقدمة", "Arabic company"),
        ("company", "Innovation Labs", "Tech company"),
        ("company", "مختبرات الابتكار", "Arabic innovation lab"),
        
        # WebApps
        ("webapp", "Learning Management System", "English webapp"),
        ("webapp", "نظام إدارة التعلم", "Arabic webapp"),
        ("webapp", "Data Analytics Tool", "Analytics webapp"),
        ("webapp", "أداة تحليل البيانات", "Arabic analytics tool"),
        
        # Categories
        ("category", "Science & Technology", "English category"),
        ("category", "العلوم والتكنولوجيا", "Arabic category"),
        ("category", "Business & Finance", "Business category"),
        ("category", "الأعمال والمالية", "Arabic business category"),
        
        # Courses
        ("course", "Introduction to Programming", "English course"),
        ("course", "مقدمة في البرمجة", "Arabic course"),
        ("course", "Advanced Mathematics", "Math course"),
        ("course", "الرياضيات المتقدمة", "Arabic math course"),
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
    
    print("\n📝 EXAMPLE AGENT RESPONSE:")
    print("-" * 40)
    print("Found 1 book(s):")
    print()
    print("📚 **Book 1:**")
    print("   📖 Title: Encyclopedia of Science")
    print("   ✍️ Author: Dr. Smith")
    print("   📋 ISBN: 978-1234567890")
    print("   📝 Description: Comprehensive guide to scientific concepts...")
    print("   📄 Pages: 500")
    print("   ⭐ Rating: 4.5/5")
    print("   🔗 Explore Book: https://msarii.com/books/encyclopedia-of-science")
    print("   👤 Author Page: https://msarii.com/authors/dr-smith")

if __name__ == "__main__":
    test_link_generation()
