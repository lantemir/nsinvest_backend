from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.text import slugify

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

    def save(self, *args, **kwargs):
        if not self.flug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="courses")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    thumbnail = models.ImageField(upload_to="course_thumbnails/", null=True, blank=True)
    def __str__(self):
        return self.title
    
class Lesson(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextUploadingField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    video = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.order + 1}. {self.title}"
    