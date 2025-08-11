import re
from django.db.models import Q
from .enhanced_models import EnhancedAuthor, EnhancedBook, Article, Category, WebApp, Company
from .link_generator import QueryResponseBuilder, ArabicLinkGenerator

class EnhancedAIAgent:
    """Enhanced AI agent with Arabic query processing and dynamic linking"""
    
    def __init__(self):
        self.response_builder = QueryResponseBuilder()
        self.link_generator = ArabicLinkGenerator()
    
    def process_query(self, query):
        """Process Arabic query and return enhanced response"""
        query = query.strip()
        
        # Determine query type based on keywords
        if any(word in query for word in ['كتاب', 'مؤلف', 'مصنف']):
            return self.handle_book_query(query)
        elif any(word in query for word in ['مؤلف', 'كاتب', 'عالم']):
            return self.handle_author_query(query)
        elif any(word in query for word in ['فئة', 'تصنيف', 'نوع']):
            return self.handle_category_query(query)
        elif any(word in query for word in ['مقال', 'بحث']):
            return self.handle_article_query(query)
        elif any(word in query for word in ['تطبيق', 'برنامج']):
            return self.handle_webapp_query(query)
        elif any(word in query for word in ['شركة', 'مؤسسة']):
            return self.handle_company_query(query)
        else:
            return self.handle_general_query(query)
    
    def extract_arabic_text(self, query):
        """Extract Arabic text from query for search"""
        # Remove common Arabic prefixes
        prefixes = ['عن', 'في', 'من', 'إلى', 'بخصوص', 'حول']
        text = query
        
        for prefix in prefixes:
            text = text.replace(prefix, '').strip()
        
        return text
    
    def handle_book_query(self, query):
        """Handle book-related queries"""
        search_text = self.extract_arabic_text(query)
        
        # Search by book title
        books = EnhancedBook.objects.filter(
            Q(title_ar__icontains=search_text) |
            Q(title__icontains=search_text)
        )
        
        if books.exists():
            book = books.first()
            return self.response_builder.build_book_response(book)
        
        # Search by author name
        authors = EnhancedAuthor.objects.filter(
            Q(name_ar__icontains=search_text) |
            Q(name__icontains=search_text)
        )
        
        if authors.exists():
            author = authors.first()
            books = EnhancedBook.objects.filter(author=author)
            if books.exists():
                return self.response_builder.build_author_response(author)
        
        return {
            'error': 'لم يتم العثور على الكتاب المطلوب',
            'suggestions': self.get_suggestions(search_text)
        }
    
    def handle_author_query(self, query):
        """Handle author-related queries"""
        search_text = self.extract_arabic_text(query)
        
        authors = EnhancedAuthor.objects.filter(
            Q(name_ar__icontains=search_text) |
            Q(name__icontains=search_text)
        )
        
        if authors.exists():
            author = authors.first()
            return self.response_builder.build_author_response(author)
        
        return {
            'error': 'لم يتم العثور على المؤلف المطلوب',
            'suggestions': self.get_suggestions(search_text)
        }
    
    def handle_category_query(self, query):
        """Handle category-related queries"""
        search_text = self.extract_arabic_text(query)
        
        categories = Category.objects.filter(
            Q(name_ar__icontains=search_text) |
            Q(name__icontains=search_text)
        )
        
        if categories.exists():
            category = categories.first()
            return self.response_builder.build_category_response(category)
        
        return {
            'error': 'لم يتم العثور على الفئة المطلوبة',
            'suggestions': self.get_suggestions(search_text)
        }
    
    def handle_article_query(self, query):
        """Handle article-related queries"""
        search_text = self.extract_arabic_text(query)
        
        articles = Article.objects.filter(
            Q(title_ar__icontains=search_text) |
            Q(title__icontains=search_text) |
            Q(content__icontains=search_text)
        )
        
        if articles.exists():
            article = articles.first()
            return {
                'title': article.title_ar,
                'summary': article.summary,
                'author': article.author.name_ar,
                'links': {
                    'article': article.get_msarii_url(),
                    'author': article.author.get_msarii_url()
                }
            }
        
        return {
            'error': 'لم يتم العثور على المقال المطلوب',
            'suggestions': self.get_suggestions(search_text)
        }
    
    def handle_webapp_query(self, query):
        """Handle webapp-related queries"""
        search_text = self.extract_arabic_text(query)
        
        webapps = WebApp.objects.filter(
            Q(name_ar__icontains=search_text) |
            Q(name__icontains=search_text) |
            Q(description__icontains=search_text)
        )
        
        if webapps.exists():
            webapp = webapps.first()
            return {
                'name': webapp.name_ar,
                'description': webapp.description,
                'links': {
                    'webapp': webapp.get_msarii_url()
                }
            }
        
        return {
            'error': 'لم يتم العثور على التطبيق المطلوب',
            'suggestions': self.get_suggestions(search_text)
        }
    
    def handle_company_query(self, query):
        """Handle company-related queries"""
        search_text = self.extract_arabic_text(query)
        
        companies = Company.objects.filter(
            Q(name_ar__icontains=search_text) |
            Q(name__icontains=search_text) |
            Q(description__icontains=search_text)
        )
        
        if companies.exists():
            company = companies.first()
            return {
                'name': company.name_ar,
                'description': company.description,
                'links': {
                    'company': company.get_msarii_url()
                }
            }
        
        return {
            'error': 'لم يتم العثور على الشركة المطلوبة',
            'suggestions': self.get_suggestions(search_text)
        }
    
    def handle_general_query(self, query):
        """Handle general queries with smart matching"""
        search_text = self.extract_arabic_text(query)
        
        # Try multiple search strategies
        results = []
        
        # Search books
        books = EnhancedBook.objects.filter(
            Q(title_ar__icontains=search_text) |
            Q(description__icontains=search_text)
        )[:3]
        
        for book in books:
            results.append({
                'type': 'book',
                'title': book.title_ar,
                'author': book.author.name_ar,
                'url': book.get_msarii_url()
            })
        
        # Search authors
        authors = EnhancedAuthor.objects.filter(
            Q(name_ar__icontains=search_text) |
            Q(bio__icontains=search_text)
        )[:3]
        
        for author in authors:
            results.append({
                'type': 'author',
                'name': author.name_ar,
                'url': author.get_msarii_url()
            })
        
        # Search articles
        articles = Article.objects.filter(
            Q(title_ar__icontains=search_text) |
            Q(content__icontains=search_text)
        )[:3]
        
        for article in articles:
            results.append({
                'type': 'article',
                'title': article.title_ar,
                'author': article.author.name_ar,
                'url': article.get_msarii_url()
            })
        
        if results:
            return {
                'results': results,
                'query': search_text,
                'total_found': len(results)
            }
        
        return {
            'error': 'لم يتم العثور على نتائج',
            'suggestions': self.get_suggestions(search_text)
        }
    
    def get_suggestions(self, search_text):
        """Get search suggestions based on partial matches"""
        suggestions = []
        
        # Suggest similar authors
        authors = EnhancedAuthor.objects.filter(
            name_ar__icontains=search_text[:3]
        )[:3]
        
        for author in authors:
            suggestions.append({
                'type': 'author',
                'name': author.name_ar,
                'url': author.get_msarii_url()
            })
        
        # Suggest similar books
        books = EnhancedBook.objects.filter(
            title_ar__icontains=search_text[:3]
        )[:3]
        
        for book in books:
            suggestions.append({
                'type': 'book',
                'title': book.title_ar,
                'url': book.get_msarii_url()
            })
        
        return suggestions
    
    def generate_contextual_response(self, entity_type, entity_id):
        """Generate contextual response with all related links"""
        if entity_type == 'book':
            book = EnhancedBook.objects.get(id=entity_id)
            return self.response_builder.build_book_response(book)
        elif entity_type == 'author':
            author = EnhancedAuthor.objects.get(id=entity_id)
            return self.response_builder.build_author_response(author)
        elif entity_type == 'category':
            category = Category.objects.get(id=entity_id)
            return self.response_builder.build_category_response(category)
        
        return {'error': 'نوع الكيان غير معروف'}
