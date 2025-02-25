from rest_framework import serializers
from .models import ChatRoom, Message
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
import random
from .models import EmailVerificationCode
from .tasks import send_verification_email  # Импорт задачи Celery



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Сначала пытаемся найти пользователя по `username`
        try:
            user = User.objects.get(username=attrs["username"])
        except User.DoesNotExist:
            raise AuthenticationFailed("Неправильный логин или пароль", code="authorization_failed")

        # Проверяем, активирован ли пользователь перед аутентификацией
        if not user.is_active:
            # Генерируем новый код подтверждения
            verification_code = str(random.randint(100000, 999999))

            # Обновляем или создаем код в базе
            code_obj, created = EmailVerificationCode.objects.update_or_create(
                user=user, defaults={"code": verification_code}
            )

            # Отправляем код пользователю через Celery
            send_verification_email.delay(user.email, verification_code)

            raise AuthenticationFailed(
                "Подтвердите email перед входом. Новый код отправлен на вашу почту.", 
                code="user_inactive"
            )

        # Теперь аутентифицируем пользователя (логин + пароль)
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if user is None:
            raise AuthenticationFailed("Неправильный логин или пароль", code="authorization_failed")

        # Передаем пользователя в стандартный механизм SimpleJWT
        data = super().validate(attrs)

        # Добавляем user ID в response
        data["user"] = {
            "id": user.id,
            "username": user.username,
        }
        print("data@@@", data)
        return data


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = "__all__"

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"
        extra_kwargs = {"user": {"read_only": True}}  # Добавляем

# Сериализатор для регистрации

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Этот логин уже используется.")]
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Этот email уже зарегистрирован.")]
    )

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}
# class UserSerializer(serializers.ModelSerializer):  

#     class Meta:
#         model = User
#         fields = ["id", "username", "email", "password"]
#         extra_kwargs = {"password": {"write_only": True}}

#     def create(self, validated_data):
#         validated_data["password"] = make_password(validated_data["password"])
#         return super().create(validated_data)
    
