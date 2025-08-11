import re
import unidecode
from django.utils.text import slugify

class ArabicLinkGenerator:
    """Generate SEO-friendly Arabic URLs for msarii.com"""
    
    BASE_URLS = {
        'author': 'https://msarii.com/authors/',
        'book': 'https://msarii.com/book-detail/',
        'category': 'https://msarii.com/categories/',
        'article': 'https://msarii.com/articles/',
        'webapp': 'https://msarii.com/webapps/detail/',
        'company': 'https://msarii.com/webapps/companies/'
    }
    
    @staticmethod
    def arabic_slugify(text):
        """Convert Arabic text to URL-friendly slug"""
        if not text:
            return ''
        
        # Remove Arabic diacritics
        text = re.sub(r'[\u064B-\u0652\u0640]', '', text)
        
        # Replace Arabic characters with Latin equivalents
        arabic_to_latin = {
            'ا': 'a', 'أ': 'a', 'إ': 'a', 'آ': 'a',
            'ب': 'b', 'ت': 't', 'ث': 'th', 'ج': 'j',
            'ح': 'h', 'خ': 'kh', 'د': 'd', 'ذ': 'dh',
            'ر': 'r', 'ز': 'z', 'س': 's', 'ش': 'sh',
            'ص': 's', 'ض': 'd', 'ط': 't', 'ظ': 'z',
            'ع': 'a', 'غ': 'gh', 'ف': 'f', 'ق': 'q',
            'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n',
            'ه': 'h', 'و': 'w', 'ي': 'y', 'ى': 'a'
        }
        
        for arabic, latin in arabic_to_latin.items():
            text = text.replace(arabic, latin)
        
        # Use Django's slugify for remaining processing
        return slugify(text)
    
    @classmethod
    def generate_url(cls, content_type, title_ar, slug=None):
        """Generate complete URL for content"""
        if slug:
            slug = cls.arabic_slugify(slug)
        else:
            slug = cls.arabic_slugify(title_ar)
        
        base_url = cls.BASE_URLS.get(content_type, '')
        return f"{base_url}{slug}"
    
    @classmethod
    def generate_contextual_links(cls, entity, related_entities=None):
        """Generate contextual links based on entity type"""
        links = {}
        
        if hasattr(entity, 'get_msarii_url'):
            links['main'] = entity.get_msarii_url()
        
        # Generate related links
        if related_entities:
            links['related'] = []
            for related in related_entities:
                if hasattr(related, 'get_msarii_url'):
                    links['related'].append({
                        'title': str(related),
                        'url': related.get_msarii_url()
                    })
        
        return links

class QueryResponseBuilder:
    """Build enhanced responses with dynamic linking"""
    
    @staticmethod
    def build_book_response(book):
        """Build response for book queries"""
        response = {
            'title': book.title_ar,
            'author': book.author.name_ar,
            'description': book.description,
            'links': {
                'book': book.get_msarii_url(),
                'author': book.get_author_url(),
                'related_books': []
            }
        }
        
        # Add related books by same author
        related_books = EnhancedBook.objects.filter(
            author=book.author
        ).exclude(id=book.id)[:5]
        
        for related in related_books:
            response['links']['related_books'].append({
                'title': related.title_ar,
                'url': related.get_msarii_url()
            })
        
        return response
    
    @staticmethod
    def build_author_response(author):
        """Build response for author queries"""
        response = {
            'name': author.name_ar,
            'bio': author.bio,
            'links': {
                'author': author.get_msarii_url(),
                'books': [],
                'articles': []
            }
        }
        
        # Add books
        books = EnhancedBook.objects.filter(author=author)
        for book in books:
            response['links']['books'].append({
                'title': book.title_ar,
                'url': book.get_msarii_url()
            })
        
        # Add articles
        articles = Article.objects.filter(author=author)
        for article in articles:
            response['links']['articles'].append({
                'title': article.title_ar,
                'url': article.get_msarii_url()
            })
        
        return response
    
    @staticmethod
    def build_category_response(category):
        """Build response for category queries"""
        response = {
            'category': category.name_ar,
            'description': category.description,
            'links': {
                'category': f"https://msarii.com/categories/{category.slug}",
                'books': [],
                'articles': []
            }
        }
        
        # Add books in category
        books = EnhancedBook.objects.filter(categories=category)
        for book in books:
            response['links']['books'].append({
                'title': book.title_ar,
                'author': book.author.name_ar,
                'url': book.get_msarii_url()
            })
        
        return response
