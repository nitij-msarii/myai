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
        query = (query or '').strip()
        
        # Normalize Arabic punctuation/spaces
        query = re.sub(r"[\u061F\u060C,.;!?]+", " ", query)
        query = re.sub(r"\s+", " ", query).strip()

        # Route based on intent keywords/patterns
        # Books: كتاب/كتب or explicit request for a book
        if re.search(r"\b(كتاب|كتب)\b", query):
            # If it's "كتب <category>" route to category
            if re.search(r"\bكتب\b", query) and not re.search(r"\bكتاب\b", query):
                return self.handle_category_query(query)
            return self.handle_book_query(query)
        
        # Authors: mentions of author or pattern "من هو <name>"
        if re.search(r"\b(مؤلف|كاتب|عالم)\b", query) or re.search(r"^من\s+هو\s+", query):
            return self.handle_author_query(query)
        
        # Categories: explicit category terms
        if re.search(r"\b(فئة|تصنيف|نوع)\b", query):
            return self.handle_category_query(query)
        
        # Articles (singular/plural)
        if re.search(r"\b(مقال|مقالات|بحث)\b", query):
            return self.handle_article_query(query)
        
        # Webapps (singular/plural)
        if re.search(r"\b(تطبيق|تطبيقات|برنامج|برامج)\b", query):
            return self.handle_webapp_query(query)
        
        # Companies (singular/plural)
        if re.search(r"\b(شركة|شركات|مؤسسة)\b", query):
            return self.handle_company_query(query)
        
        return self.handle_general_query(query)
    
    def extract_arabic_text(self, query):
        """Extract Arabic text from query for search: remove stopwords and intent words"""
        text = (query or '')
        
        # Common fillers/stop words and intent markers to drop
        stopwords = [
            'عن','في','من','الى','إلى','بخصوص','حول','على','مع','هو','هي','هذا','هذه','ذلك','تلك',
            'اريد','أريد','معلومات','رجاء','لو سمحت','من هو','من',
            # intent/type tokens
            'كتاب','كتب','مؤلف','كاتب','عالم','مقال','مقالات','بحث','تطبيق','تطبيقات','برنامج','برامج','شركة','شركات','مؤسسة',
            'فئة','تصنيف','نوع'
        ]
        # Remove combined phrases first
        for phrase in ['من هو']:
            text = re.sub(rf"\b{re.escape(phrase)}\b", " ", text)
        # Then single-token removals
        for sw in stopwords:
            text = re.sub(rf"\b{re.escape(sw)}\b", " ", text)
        # Remove punctuation and extra spaces
        text = re.sub(r"[\u061F\u060C,.;!?]+", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text
    
    def handle_book_query(self, query):
        """Handle book-related queries"""
        search_text = self.extract_arabic_text(query)
        
        # Search by book title or partials
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
        
        # Try by category name (e.g., "كتب الفقه الإسلامي")
        categories = Category.objects.filter(
            Q(name_ar__icontains=search_text) |
            Q(name__icontains=search_text)
        )
        if categories.exists():
            category = categories.first()
            return self.response_builder.build_category_response(category)
        
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
        
        # Suggest similar categories
        categories = Category.objects.filter(
            name_ar__icontains=search_text[:3]
        )[:3]
        for cat in categories:
            suggestions.append({
                'type': 'category',
                'name': cat.name_ar,
                'url': f"https://msarii.com/categories/{cat.slug}"
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
