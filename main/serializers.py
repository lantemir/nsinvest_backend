from rest_framework import serializers
from .models import ChatRoom, Message
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
import random
from .models import EmailVerificationCode, Profile, Category, Course, Lesson, Interesting, Book, Meeting
from .tasks import send_verification_email  # Импорт задачи Celery



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["user_id"] = user.id

        return token

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
    

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["avatar", "phone_number"]
    
    def validate_avatar(self, value):
        # Проверка размера
        if value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("Максимальный размер файла — 2MB")
        
        # Проверка расширения
        valid_extensions = (".jpg", ".jpeg", ".png")
        if not value.name.lower().endswith(valid_extensions):
            raise serializers.ValidationError("Допустимые форматы: JPG, JPEG, PNG")

        return value

class CurrentUserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    class Meta:
        model = User
        fields =["id", "username", "email", "profile"]    


class UserProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ["id", "username", "email", "profile"]
    # instance=request.user — объект, который обновляем.    data=request.data — данные от клиента.
    def update(self, instance, validate_date):  
        profile_data = validate_date.pop("profile", {})
        profile = instance.profile

        instance.username = validate_date.get("username", instance.username)
        instance.email = validate_date.get("email", instance.email)
        instance.save()

        profile.phone_number = profile_data.get("phone_number", None)
        avatar =profile_data.get("avatar", None)

        if avatar:
            profile.avatar = avatar
        profile.save()

        return instance

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"

class InterestingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interesting
        fields = "__all__"


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"

class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields= "__all__"



        

