from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=200, verbose_name="الاسم")
    bio = models.TextField(blank=True, verbose_name="السيرة الذاتية")
    link = models.URLField(blank=True, verbose_name="الرابط")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "مؤلف"
        verbose_name_plural = "المؤلفون"
    
    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=300, verbose_name="العنوان")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name="المؤلف")
    isbn = models.CharField(max_length=20, blank=True, verbose_name="ISBN")
    description = models.TextField(blank=True, verbose_name="الوصف")
    link = models.URLField(blank=True, verbose_name="الرابط")
    genre = models.CharField(max_length=100, blank=True, verbose_name="النوع")
    publication_date = models.DateField(null=True, blank=True, verbose_name="تاريخ النشر")
    pages = models.IntegerField(null=True, blank=True, verbose_name="عدد الصفحات")
    language = models.CharField(max_length=50, default="العربية", verbose_name="اللغة")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "كتاب"
        verbose_name_plural = "الكتب"
    
    def __str__(self):
        return f"{self.title} - {self.author.name}"

class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان الدورة")
    description = models.TextField(blank=True, verbose_name="الوصف")
    instructor = models.CharField(max_length=100, blank=True, verbose_name="المعلم")
    link = models.URLField(blank=True, verbose_name="الرابط")
    duration = models.CharField(max_length=50, blank=True, verbose_name="المدة")
    level = models.CharField(max_length=50, blank=True, verbose_name="المستوى")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "دورة تعليمية"
        verbose_name_plural = "الدورات التعليمية"
    
    def __str__(self):
        return self.title

class User(models.Model):
    username = models.CharField(max_length=100, unique=True, verbose_name="اسم المستخدم")
    email = models.EmailField(unique=True, verbose_name="البريد الإلكتروني")
    full_name = models.CharField(max_length=200, verbose_name="الاسم الكامل")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمون"
    
    def __str__(self):
        return self.full_name

# Ensure enhanced models are registered with Django's app registry for migrations
# by importing them here.
try:
    from .enhanced_models import Category, EnhancedAuthor, EnhancedBook, Article, WebApp, Company  # noqa: F401
except Exception:
    # During initial migration generation, this import may fail if dependencies are missing.
    # It's safe to ignore here because the enhanced models will be imported when available.
    pass
