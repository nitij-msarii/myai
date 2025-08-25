from django.core.management.base import BaseCommand
from django.db import transaction
from AI_agent.enhanced_models import EnhancedAuthor, EnhancedBook, Category, Article, WebApp, Company
import json

class Command(BaseCommand):
    help = 'Populate enhanced database with sample Arabic data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate enhanced data...'))
        
        with transaction.atomic():
            # Create categories
            categories_data = [
                {'name_ar': 'الفقه الإسلامي', 'description': 'كتب الفقه والأحكام الشرعية'},
                {'name_ar': 'الحديث النبوي', 'description': 'كتب الحديث الشريف وعلومه'},
                {'name_ar': 'العقيدة', 'description': 'كتب العقيدة والتوحيد'},
                {'name_ar': 'السيرة النبوية', 'description': 'كتب السيرة والتاريخ الإسلامي'},
                {'name_ar': 'اللغة العربية', 'description': 'كتب اللغة والنحو والصرف'},
                {'name_ar': 'الفلسفة', 'description': 'كتب الفلسفة والفكر الإسلامي'},
            ]
            
            categories = {}
            for cat_data in categories_data:
                category, created = Category.objects.get_or_create(
                    name_ar=cat_data['name_ar'],
                    defaults={'description': cat_data['description']}
                )
                categories[cat_data['name_ar']] = category
                if created:
                    self.stdout.write(f"Created category: {cat_data['name_ar']}")
            
            # Create authors from library_authors.sql data
            authors_data = [
                {
                    'name_ar': 'ابن قيم الجوزية',
                    'bio': 'ابن قيم الجوزية (691 هـ - 751 هـ / 1292م - 1350م) هو عالم مسلم بارز من علماء المذهب الحنبلي خلال العصر المملوكي في دمشق.',
                    'profession': 'عالم دين',
                    'wikipedia': 'https://ar.wikipedia.org/wiki/ابن_قيم_الجوزية',
                    'youtube': 'https://www.youtube.com/results?search_query=كتب+ابن+القيم',
                    'slug': 'ابن-قيم-الجوزية'
                },
                {
                    'name_ar': 'الإمام النووي',
                    'bio': 'الإمام النووي هو يحيى بن شرف بن مري النووي. ولد في عام 631 هـ في نوى، جنوب دمشق وتوفي في عام 676 هـ.',
                    'profession': 'عالم دين',
                    'wikipedia': 'https://ar.wikipedia.org/wiki/النووي',
                    'youtube': 'https://www.youtube.com/results?search_query=الإمام+النووي',
                    'slug': 'الإمام-النووي'
                },
                {
                    'name_ar': 'ابن كثير الدمشقي',
                    'bio': 'عماد الدين أبو الفداء إسماعيل بن عمر بن كثير، مُحدّث ومفسر وفقيه.',
                    'profession': 'مفسر ومحدث',
                    'wikipedia': 'https://ar.wikipedia.org/wiki/ابن_كثير_الدمشقي',
                    'youtube': 'https://www.youtube.com/watch?v=O1nJvMVLY-w',
                    'slug': 'ابن-كثير-الدمشقي'
                },
                {
                    'name_ar': 'محمد أبو زهرة',
                    'bio': 'ولد محمد بن أحمد بن مصطفى بن أحمد المعروف بأبي زهرة في المحلة الكبرى التابعة لمحافظة الغربية بمصر.',
                    'profession': 'عالم دين',
                    'wikipedia': 'https://ar.wikipedia.org/wiki/محمد_أبو_زهرة',
                    'youtube': 'https://www.youtube.com/results?search_query=محمد+أبو+زهرة',
                    'slug': 'محمد-أبو-زهرة'
                }
            ]
            
            authors = {}
            for author_data in authors_data:
                author, created = EnhancedAuthor.objects.get_or_create(
                    name_ar=author_data['name_ar'],
                    defaults={
                        'bio': author_data['bio'],
                        'profession': author_data['profession'],
                        'wikipedia': author_data['wikipedia'],
                        'youtube': author_data['youtube'],
                        'slug': author_data['slug']
                    }
                )
                authors[author_data['name_ar']] = author
                if created:
                    self.stdout.write(f"Created author: {author_data['name_ar']}")
            
            # Create books
            books_data = [
                {
                    'title_ar': 'الروح',
                    'author': 'ابن قيم الجوزية',
                    'description': 'يتناول الكاتب في هذه المسائل الاجابة على الأسئلة التي تحيّر المؤمن فيما يخص أرواح الأموات وتعلقها في مرحلة البرزخ.',
                    'genre': 'العقيدة',
                    'pages': 400,
                    'categories': ['العقيدة', 'الفقه الإسلامي']
                },
                {
                    'title_ar': 'رياض الصالحين',
                    'author': 'الإمام النووي',
                    'description': 'كتاب في الحديث النبوي يحتوي على أحاديث في الأخلاق والآداب.',
                    'genre': 'الحديث النبوي',
                    'pages': 600,
                    'categories': ['الحديث النبوي', 'الأخلاق']
                },
                {
                    'title_ar': 'تفسير القرآن العظيم',
                    'author': 'ابن كثير الدمشقي',
                    'description': 'تفسير شامل للقرآن الكريم من أهم كتب التفسير.',
                    'genre': 'التفسير',
                    'pages': 3000,
                    'categories': ['التفسير', 'الحديث النبوي']
                },
                {
                    'title_ar': 'تاريخ المذاهب الإسلامية',
                    'author': 'محمد أبو زهرة',
                    'description': 'دراسة تاريخية للمذاهب الإسلامية وأعلامها.',
                    'genre': 'التاريخ',
                    'pages': 800,
                    'categories': ['الفلسفة', 'التاريخ']
                }
            ]
            
            for book_data in books_data:
                author = authors[book_data['author']]
                book, created = EnhancedBook.objects.get_or_create(
                    title_ar=book_data['title_ar'],
                    author=author,
                    defaults={
                        'description': book_data['description'],
                        'genre': book_data['genre'],
                        'pages': book_data['pages']
                    }
                )
                
                if created:
                    # Add categories
                    for cat_name in book_data['categories']:
                        if cat_name in categories:
                            book.categories.add(categories[cat_name])
                    self.stdout.write(f"Created book: {book_data['title_ar']}")
            
            # Create articles
            articles_data = [
                {
                    'title_ar': 'عالم الروايات والقصص الأدبية: رحلة في عالم الخيال والإبداع',
                    'author': 'محمد أبو زهرة',
                    'content': 'تتناول هذه المقالة عالم الروايات والقصص الأدبية، موضحةً قيمتها الثقافية وقوة السرد فيها...',
                    'summary': 'مقالة عن أهمية الروايات والقصص في الثقافة العربية',
                    'categories': ['اللغة العربية']
                },
                {
                    'title_ar': 'الفكر الإسلامي المعاصر: التحديات والآفاق',
                    'author': 'ابن قيم الجوزية',
                    'content': 'تحليل للتحديات التي يواجهها الفكر الإسلامي في العصر الحديث...',
                    'summary': 'مقالة تحليلية عن الفكر الإسلامي',
                    'categories': ['الفلسفة']
                }
            ]
            
            for article_data in articles_data:
                author = authors[article_data['author']]
                article, created = Article.objects.get_or_create(
                    title_ar=article_data['title_ar'],
                    author=author,
                    defaults={
                        'content': article_data['content'],
                        'summary': article_data['summary']
                    }
                )
                
                if created:
                    # Add categories
                    for cat_name in article_data['categories']:
                        if cat_name in categories:
                            article.categories.add(categories[cat_name])
                    self.stdout.write(f"Created article: {article_data['title_ar']}")
            
            # Create webapps
            webapps_data = [
                {
                    'name_ar': 'مدرسة محمد بن راشد الحكومية',
                    'description': 'قادة الغد هم هدف هذه الأمة وأساس مستقبلها وسنعمل على تطوير قدراتهم ومعارفهم...',
                    'url': 'https://msarii.com/webapps/detail/مدرسة-محمد-بن-راشد-الحكومية',
                    'categories': ['التعليم']
                }
            ]
            
            for webapp_data in webapps_data:
                webapp, created = WebApp.objects.get_or_create(
                    name_ar=webapp_data['name_ar'],
                    defaults={
                        'description': webapp_data['description'],
                        'url': webapp_data['url']
                    }
                )
                
                if created:
                    # Add categories
                    for cat_name in webapp_data['categories']:
                        if cat_name in categories:
                            webapp.categories.add(categories[cat_name])
                    self.stdout.write(f"Created webapp: {webapp_data['name_ar']}")
            
            # Create companies
            companies_data = [
                {
                    'name_ar': 'Msarii',
                    'description': 'Public Library & Webapp Portal',
                    'website': 'https://msarii.com',
                }
            ]
            
            for company_data in companies_data:
                company, created = Company.objects.get_or_create(
                    name_ar=company_data['name_ar'],
                    defaults={
                        'description': company_data['description'],
                        'website': company_data['website']
                    }
                )
                
                if created:
                    self.stdout.write(f"Created company: {company_data['name_ar']}")
        
        self.stdout.write(self.style.SUCCESS('Successfully populated enhanced data!'))
