from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field


# Create your models here.

# class UploadedImage(models.Model):
#     image = models.ImageField(upload_to="uploads/")
#     uploaded_at = models.DateTimeField(auto_now_add=True)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"

#сигнал при создании юзера автоматом создаст таблицу profile 
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # тут происходит первое создание модели
        Profile.objects.get_or_create(user=instance) 
   

class InvestmentProject(models.Model):
    name = models.CharField(max_length=255)  # Название инвестиции
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Сумма
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания

    def __str__(self):
        return self.name
    
class ChatRoom(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to="chat_images/", null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"
    
class ImageModel(models.Model):
    file = models.ImageField(upload_to="images/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
    
class EmailVerificationCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="verification_code")
    code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)  # Флаг для отслеживания использованного кода

    def __str__(self):
        return f"Код {self.code} для {self.user.username}"
    
    def is_expired(self): 
        """ Код считается просроченным через 10 минут """
        return (now() - self.created_at).total_seconds() > 600

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    path = models.CharField(max_length=100, unique=True, blank=True, null=True, help_text="Путь для фронта (например: programming, eng-basic)" )
    order = models.PositiveSmallIntegerField(default=0, help_text="Чем меньше значение — тем выше категория")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.path:
            self.path = self.slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['order']  
    
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="courses")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    thumbnail = models.ImageField(upload_to="course_thumbnails/", null=True, blank=True)
    def __str__(self):
        return self.title
    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ['-created_at', '-id']
    
class Lesson(models.Model):
    title = models.CharField(max_length=200)
    content = CKEditor5Field('Text', config_name='default')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    video = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["course", "order"]

    def __str__(self):
        return f"{self.course} - {self.order} - {self.title}"
    
class Interesting(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name="category", null=True, blank=True)
    content = CKEditor5Field('Text', config_name='default')
    video = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    cover = models.ImageField(upload_to="interesting/cover/", blank=True, null=True)

    def __str__(self) -> str:
        return self.title  # <-- то, что увидишь в списке в админке
    class Meta:
        verbose_name = "Интересное"
        verbose_name_plural = "Интересные"
        ordering = ['-created_at', '-id']

class Book(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="books/")
    cover = models.ImageField(upload_to="books/cover/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.category} - {self.title}"
    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        ordering = ['-created_at', '-id']
    
class Meeting(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    start_time = models.TimeField()
    end_time =  models.TimeField()
    youtube_link = models.TextField(blank=True, null=True)
    zoom_link = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.date})"    
    
    class Meta:
        verbose_name = "Календарь"
        verbose_name_plural = "Календарь событий"
        ordering = ['-date', '-id']