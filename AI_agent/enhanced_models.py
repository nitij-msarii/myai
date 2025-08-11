from django.db import models
from django.utils.text import slugify
import unidecode

class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name="الاسم")
    name_ar = models.CharField(max_length=200, verbose_name="الاسم العربي")
    description = models.TextField(blank=True, verbose_name="الوصف")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "فئة"
        verbose_name_plural = "الفئات"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode.unidecode(self.name_ar))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name_ar

class EnhancedAuthor(models.Model):
    name = models.CharField(max_length=200, verbose_name="الاسم")
    name_ar = models.CharField(max_length=200, verbose_name="الاسم العربي")
    bio = models.TextField(blank=True, verbose_name="السيرة الذاتية")
    profession = models.CharField(max_length=100, blank=True, verbose_name="المهنة")
    profile_pic = models.ImageField(upload_to='library_authors/', blank=True)
    wikipedia = models.URLField(blank=True, verbose_name="ويكيبيديا")
    youtube = models.URLField(blank=True, verbose_name="يوتيوب")
    twitter = models.URLField(blank=True, verbose_name="تويتر")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    short_url = models.URLField(blank=True, verbose_name="الرابط المختصر")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "مؤلف"
        verbose_name_plural = "المؤلفون"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode.unidecode(self.name_ar))
        super().save(*args, **kwargs)
    
    def get_msarii_url(self):
        return f"https://msarii.com/authors/{self.slug}"
    
    def __str__(self):
        return self.name_ar

class EnhancedBook(models.Model):
    title = models.CharField(max_length=300, verbose_name="العنوان")
    title_ar = models.CharField(max_length=300, verbose_name="العنوان العربي")
    author = models.ForeignKey(EnhancedAuthor, on_delete=models.CASCADE, verbose_name="المؤلف")
    description = models.TextField(blank=True, verbose_name="الوصف")
    isbn = models.CharField(max_length=20, blank=True, verbose_name="ISBN")
    genre = models.CharField(max_length=100, blank=True, verbose_name="النوع")
    pages = models.IntegerField(null=True, blank=True, verbose_name="عدد الصفحات")
    language = models.CharField(max_length=50, default="العربية", verbose_name="اللغة")
    publication_date = models.DateField(null=True, blank=True, verbose_name="تاريخ النشر")
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    categories = models.ManyToManyField(Category, blank=True, verbose_name="الفئات")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "كتاب"
        verbose_name_plural = "الكتب"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode.unidecode(self.title_ar))
        super().save(*args, **kwargs)
    
    def get_msarii_url(self):
        return f"https://msarii.com/book-detail/{self.slug}"
    
    def get_author_url(self):
        return self.author.get_msarii_url()
    
    def __str__(self):
        return f"{self.title_ar} - {self.author.name_ar}"

class Article(models.Model):
    title = models.CharField(max_length=300, verbose_name="العنوان")
    title_ar = models.CharField(max_length=300, verbose_name="العنوان العربي")
    content = models.TextField(verbose_name="المحتوى")
    author = models.ForeignKey(EnhancedAuthor, on_delete=models.CASCADE, verbose_name="المؤلف")
    summary = models.TextField(blank=True, verbose_name="الملخص")
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    categories = models.ManyToManyField(Category, blank=True, verbose_name="الفئات")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "مقال"
        verbose_name_plural = "المقالات"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode.unidecode(self.title_ar))
        super().save(*args, **kwargs)
    
    def get_msarii_url(self):
        return f"https://msarii.com/articles/{self.slug}"
    
    def __str__(self):
        return self.title_ar

class WebApp(models.Model):
    name = models.CharField(max_length=200, verbose_name="الاسم")
    name_ar = models.CharField(max_length=200, verbose_name="الاسم العربي")
    description = models.TextField(verbose_name="الوصف")
    url = models.URLField(verbose_name="الرابط")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    categories = models.ManyToManyField(Category, blank=True, verbose_name="الفئات")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "تطبيق ويب"
        verbose_name_plural = "تطبيقات الويب"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode.unidecode(self.name_ar))
        super().save(*args, **kwargs)
    
    def get_msarii_url(self):
        return f"https://msarii.com/webapps/detail/{self.slug}"
    
    def __str__(self):
        return self.name_ar

class Company(models.Model):
    name = models.CharField(max_length=200, verbose_name="الاسم")
    name_ar = models.CharField(max_length=200, verbose_name="الاسم العربي")
    description = models.TextField(verbose_name="الوصف")
    website = models.URLField(blank=True, verbose_name="الموقع")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "شركة"
        verbose_name_plural = "الشركات"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode.unidecode(self.name_ar))
        super().save(*args, **kwargs)
    
    def get_msarii_url(self):
        return f"https://msarii.com/webapps/companies/{self.slug}"
    
    def __str__(self):
        return self.name_ar
