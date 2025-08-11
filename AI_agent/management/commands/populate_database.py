from django.core.management.base import BaseCommand
from AI_agent.models import Author, Book, Course, User
from datetime import date

class Command(BaseCommand):
    help = 'Populate database with sample Arabic data for testing the AI agent'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database population...'))
        
        # Clear existing data
        Book.objects.all().delete()
        Author.objects.all().delete()
        Course.objects.all().delete()
        User.objects.all().delete()
        
        # Create Authors
        authors_data = [
            {
                'name': 'أحمد شوقي',
                'bio': 'شاعر مصري كبير، لُقب بأمير الشعراء، من أعظم شعراء العربية في العصر الحديث'
            },
            {
                'name': 'نجيب محفوظ',
                'bio': 'روائي مصري حائز على جائزة نوبل للآداب، من أشهر الكتاب العرب'
            },
            {
                'name': 'طه حسين',
                'bio': 'أديب وناقد مصري، لُقب بعميد الأدب العربي'
            },
            {
                'name': 'محمد عبده',
                'bio': 'مفكر إسلامي ومجدد ديني مصري، من رواد النهضة العربية'
            },
            {
                'name': 'ابن خلدون',
                'bio': 'مؤرخ وعالم اجتماع عربي، مؤسس علم الاجتماع الحديث'
            }
        ]
        
        authors = []
        for author_data in authors_data:
            author = Author.objects.create(**author_data)
            authors.append(author)
            self.stdout.write(f'Created author: {author.name}')
        
        # Create Books
        books_data = [
            {
                'title': 'الأسود يليق بك',
                'author': authors[1],  # نجيب محفوظ
                'isbn': '978-977-416-123-4',
                'description': 'رواية تتناول قضايا المجتمع المصري المعاصر',
                'genre': 'رواية',
                'publication_date': date(1985, 3, 15),
                'pages': 280,
                'language': 'العربية'
            },
            {
                'title': 'أولاد حارتنا',
                'author': authors[1],  # نجيب محفوظ
                'isbn': '978-977-416-456-7',
                'description': 'رواية رمزية تحكي قصة الإنسانية من خلال حارة مصرية',
                'genre': 'رواية',
                'publication_date': date(1959, 12, 1),
                'pages': 450,
                'language': 'العربية'
            },
            {
                'title': 'الأيام',
                'author': authors[2],  # طه حسين
                'isbn': '978-977-416-789-1',
                'description': 'سيرة ذاتية تحكي قصة الكاتب من الطفولة إلى الشباب',
                'genre': 'سيرة ذاتية',
                'publication_date': date(1929, 6, 10),
                'pages': 320,
                'language': 'العربية'
            },
            {
                'title': 'مقدمة ابن خلدون',
                'author': authors[4],  # ابن خلدون
                'isbn': '978-977-416-012-3',
                'description': 'كتاب في التاريخ وعلم الاجتماع، يعتبر من أهم الكتب في التراث العربي',
                'genre': 'تاريخ وعلوم اجتماعية',
                'publication_date': date(1377, 1, 1),
                'pages': 600,
                'language': 'العربية'
            },
            {
                'title': 'الإسلام والنصرانية مع العلم والمدنية',
                'author': authors[3],  # محمد عبده
                'isbn': '978-977-416-345-6',
                'description': 'كتاب يناقش العلاقة بين الدين والعلم والحضارة',
                'genre': 'فكر إسلامي',
                'publication_date': date(1902, 8, 20),
                'pages': 180,
                'language': 'العربية'
            },
            {
                'title': 'ديوان شوقي',
                'author': authors[0],  # أحمد شوقي
                'isbn': '978-977-416-678-9',
                'description': 'مجموعة شعرية تضم أشهر قصائد أمير الشعراء',
                'genre': 'شعر',
                'publication_date': date(1920, 4, 5),
                'pages': 400,
                'language': 'العربية'
            }
        ]
        
        for book_data in books_data:
            book = Book.objects.create(**book_data)
            self.stdout.write(f'Created book: {book.title}')
        
        # Create Courses
        courses_data = [
            {
                'title': 'مقدمة في الأدب العربي',
                'description': 'دورة شاملة تغطي تاريخ الأدب العربي من العصر الجاهلي إلى العصر الحديث',
                'instructor': 'د. فاطمة الزهراء',
                'duration': '12 أسبوع',
                'level': 'مبتدئ'
            },
            {
                'title': 'تحليل النصوص الأدبية',
                'description': 'دورة متقدمة في تحليل النصوص الشعرية والنثرية',
                'instructor': 'د. محمد الأمين',
                'duration': '8 أسابيع',
                'level': 'متقدم'
            },
            {
                'title': 'الكتابة الإبداعية',
                'description': 'تعلم فنون الكتابة الإبداعية والسرد',
                'instructor': 'أ. سارة أحمد',
                'duration': '10 أسابيع',
                'level': 'متوسط'
            },
            {
                'title': 'تاريخ الحضارة الإسلامية',
                'description': 'دراسة شاملة لتاريخ الحضارة الإسلامية وإنجازاتها',
                'instructor': 'د. عبد الرحمن الطيب',
                'duration': '16 أسبوع',
                'level': 'متوسط'
            }
        ]
        
        for course_data in courses_data:
            course = Course.objects.create(**course_data)
            self.stdout.write(f'Created course: {course.title}')
        
        # Create Users
        users_data = [
            {
                'username': 'ahmed_ali',
                'email': 'ahmed.ali@example.com',
                'full_name': 'أحمد علي محمد'
            },
            {
                'username': 'fatima_hassan',
                'email': 'fatima.hassan@example.com',
                'full_name': 'فاطمة حسن إبراهيم'
            },
            {
                'username': 'omar_salem',
                'email': 'omar.salem@example.com',
                'full_name': 'عمر سالم أحمد'
            }
        ]
        
        for user_data in users_data:
            user = User.objects.create(**user_data)
            self.stdout.write(f'Created user: {user.full_name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated database with:\n'
                f'- {len(authors)} authors\n'
                f'- {len(books_data)} books\n'
                f'- {len(courses_data)} courses\n'
                f'- {len(users_data)} users'
            )
        )
