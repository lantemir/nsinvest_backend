from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Create your models here.

# class UploadedImage(models.Model):
#     image = models.ImageField(upload_to="uploads/")
#     uploaded_at = models.DateTimeField(auto_now_add=True)

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