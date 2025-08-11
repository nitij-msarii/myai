# Enhanced Arabic Library AI Agent

## Overview
This enhanced AI agent provides comprehensive Arabic query processing with dynamic linking capabilities for the msarii.com library system. It supports books, authors, categories, articles, webapps, and companies with SEO-friendly Arabic URLs.

## Features

### 🔗 Dynamic Linking System
- **SEO-friendly Arabic URLs** for all content types
- **Cross-referencing** between related entities
- **Contextual responses** with embedded links
- **Smart query processing** in Arabic

### 📚 Content Types Supported
- **Books**: Complete book details with author links
- **Authors**: Comprehensive author profiles with book listings
- **Categories**: Category browsing with content listings
- **Articles**: Article search with author attribution
- **WebApps**: Educational and utility applications
- **Companies**: Organization profiles and descriptions

### 🌐 URL Structure
```
Authors: https://msarii.com/authors/{arabic-slug}
Books: https://msarii.com/book-detail/{arabic-slug}
Categories: https://msarii.com/categories/{arabic-slug}
Articles: https://msarii.com/articles/{arabic-slug}
WebApps: https://msarii.com/webapps/detail/{arabic-slug}
Companies: https://msarii.com/webapps/companies/{arabic-slug}
```

## Installation & Setup

### 1. Install Dependencies
```bash
pip install django unidecode
```

### 2. Database Setup
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Populate with sample data
python manage.py populate_enhanced_data
```

### 3. Test the Agent
```bash
# Run comprehensive tests
python test_enhanced_agent.py
```

## Usage Examples

### Book Queries
```python
from AI_agent.enhanced_agent import EnhancedAIAgent

agent = EnhancedAIAgent()
response = agent.process_query("أريد معلومات عن كتاب الروح")
# Returns: Book details + author link + related books
```

### Author Queries
```python
response = agent.process_query("من هو ابن قيم الجوزية")
# Returns: Author bio + list of books + external links
```

### Category Queries
```python
response = agent.process_query("أريد كتب الفقه الإسلامي")
# Returns: Category info + books in category
```

## Arabic Query Support

### Supported Keywords
- **كتاب** (book) - Book-related queries
- **مؤلف** (author) - Author-related queries
- **فئة** (category) - Category browsing
- **مقال** (article) - Article search
- **تطبيق** (webapp) - Application search
- **شركة** (company) - Company search

### Example Queries
```
"أريد معلومات عن كتاب الروح لابن قيم الجوزية"
"من هو محمد أبو زهرة ومؤلفاته"
"أريد كتب الفقه الحنفي"
"مقالات عن الفكر الإسلامي"
"تطبيقات تعليمية"
```

## API Response Format

### Book Response
```json
{
  "title": "الروح",
  "author": "ابن قيم الجوزية",
  "description": "وصف الكتاب...",
  "links": {
    "book": "https://msarii.com/book-detail/الروح-للإمام-ابن-قيم-الجوزية",
    "author": "https://msarii.com/authors/ابن-قيم-الجوزية",
    "related_books": [
      {
        "title": "زاد المعاد",
        "url": "https://msarii.com/book-detail/زاد-المعاد"
      }
    ]
  }
}
```

### Author Response
```json
{
  "name": "ابن قيم الجوزية",
  "bio": "سيرة المؤلف...",
  "links": {
    "author": "https://msarii.com/authors/ابن-قيم-الجوزية",
    "books": [
      {
        "title": "الروح",
        "url": "https://msarii.com/book-detail/الروح"
      }
    ],
    "articles": [...]
  }
}
```

## File Structure
```
AI_agent/
├── enhanced_models.py      # Enhanced database models
├── enhanced_agent.py       # AI agent logic
├── link_generator.py       # URL generation utilities
├── management/
│   └── commands/
│       └── populate_enhanced_data.py  # Data population script
└── tests/
    └── test_enhanced_agent.py         # Test suite
```

## Testing
Run the comprehensive test suite:
```bash
python test_enhanced_agent.py
```

This will test:
- Arabic query processing
- Dynamic link generation
- Cross-referencing accuracy
- Response formatting

## Contributing
1. Add new content types to enhanced_models.py
2. Update link_generator.py for new URL patterns
3. Add test cases to test_enhanced_agent.py
4. Update populate_enhanced_data.py for sample data

## Troubleshooting
- Ensure Arabic text encoding is UTF-8
- Check database collation for Arabic support
- Verify slug generation for Arabic text
- Test URL encoding for Arabic characters

## Performance Tips
- Use database indexing for Arabic text fields
- Implement caching for frequently accessed URLs
- Optimize query patterns for large datasets
- Consider full-text search for Arabic content
