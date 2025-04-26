# from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from .models import ChatRoom,EmailVerificationCode
from .serializers import (ChatRoomSerializer, UserSerializer, CurrentUserSerializer, 
                          UserProfileSerializer, CategorySerializer, CourseSerializer, LessonSerializer)

from .models import ImageModel
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password
import random
from rest_framework.exceptions import ValidationError
from django.core.mail import send_mail, BadHeaderError
import logging
from smtplib import SMTPException
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .tasks import send_verification_email
from.serializers import CustomTokenObtainPairSerializer
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination

from .models import Category, Course, Lesson






# class ChatRoomListCreateView(generics.ListCreateAPIView):
#     queryset = ChatRoom.objects.all()
#     serializer_class = ChatRoomSerializer
#     permission_classes = [IsAuthenticated]  # Доступ только авторизованным
#     print("ChatRoomListCreateView@@@")

# class MessageListCreateView(generics.ListCreateAPIView):
#     queryset = Message.objects.all()
#     serializer_class = MessageSerializer
#     parser_classes = (MultiPartParser, FormParser)  # Позволяет загружать файлы
#     permission_classes = [IsAuthenticated]  # Доступ только авторизованным

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)


    
# Эндпоинт для регистрации
@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(generics.CreateAPIView):
    print("RegisterView@@@")
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        email = serializer.validated_data.get("email")
        print(email, "email@@@")
        if not email:
            raise ValidationError({"email": "Email обязателен."})  # Проверяем email ДО создания user

        user = serializer.save(password=make_password(serializer.validated_data["password"]), is_active=False)
        print(user, "user@@@")
        # Генерация и сохранение кода
        verification_code = str(random.randint(100000, 999999))
        EmailVerificationCode.objects.create(user=user, code=verification_code)

        # Отправка письма
        send_verification_email.delay(email, verification_code)

        # try:
        #     send_mail(
        #             "Код подтверждения",
        #             f"Ваш код подтверждения: {verification_code}",
        #             "lan888developer@gmail.com",  # Должен совпадать с EMAIL_HOST_USER
        #             [user.email],
        #             fail_silently=False,
        #         )
        #     print(f"📩 Письмо отправлено на {user.email} с кодом: {verification_code}")
        # except (BadHeaderError, SMTPException) as e:
        #     print(f"❌ Ошибка отправки письма: {e}")
        #     return Response(
        #         {"error": "Не удалось отправить письмо. Проверьте настройки почты."},
        #         status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #     )
   

# подтверждение по почте
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("Запрос на подтверждение email:", request.data)  # ✅ Логируем request.data

        email = request.data.get("email")
        code = request.data.get("code") 

        if not email or not code:  # ✅ Проверяем, что email и code переданы
            return Response({"error": "Email и код обязательны"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Пользователь не найден"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            verification_code = EmailVerificationCode.objects.get(user=user, code=code)
        except EmailVerificationCode.DoesNotExist:
            return Response({"error": "Неверный код подтверждения"}, status=status.HTTP_400_BAD_REQUEST)
        
         # Проверяем, не был ли уже использован код
        if verification_code.used:
            return Response({"error": "Этот код уже использован"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Проверяем, не истек ли код
        if verification_code.is_expired():
            return Response({"error":"Срок действия кода истек"}, status=status.HTTP_400_BAD_REQUEST)

        # Код верный → Активируем пользователя
        user.is_active = True
        user.save()

           # Отмечаем код как использованный
        verification_code.used = True
        verification_code.save()



        # # Удаляем код подтверждения
        # verification_code.delete()

        return Response({"message": "Email подтвержден"}, status=status.HTTP_200_OK)
    
class ResendVerificationCodeView(APIView):
    """
    Повторная отправка кода подтверждения
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Пользователь с таким email не найден"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Удаляем все старые коды (если разрешено хранить несколько)
        EmailVerificationCode.objects.filter(user=user).delete()

        new_code = str(random.randint(100000, 999999))

        # Создаем новый код
        EmailVerificationCode.objects.create(user=user, code=new_code)

        # # Обновляем или создаем код подтверждения
        # code_obj, created = EmailVerificationCode.objects.update_or_create(
        #     user=user, defaults={"code": new_code}
        # )

        send_verification_email.delay(email, new_code)

        # send_mail(
        #             "Код подтверждения",
        #             f"Ваш код подтверждения: {new_code}",
        #             "lan888developer@gmail.com",  # Должен совпадать с EMAIL_HOST_USER
        #             [email],
        #             fail_silently=False,
        #         )

        return Response({"message": "Код подтверждения отправлен повторно"}, status=status.HTTP_200_OK)
    
    

# Эндпоинт для получения JWT-токенов
class CustomTokenObtainPairView(TokenObtainPairView):

    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
         # Берем `refresh` токен из ответа
        refresh_token = response.data.pop("refresh", None)

        # Устанавливаем `refresh` токен в `httpOnly` cookie
        if refresh_token:
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=settings.DEBUG is False,
                samesite="Lax",
                max_age=60 * 60 * 24 *7,
            )
        return response


class CustomTokenRefreshView(APIView):
    def post(self, request, *args, **kwargs):
        """
        Принимает `refresh_token` из httpOnly cookie вместо тела запроса.
        """
        """
        Обновляет `access_token` и одновременно обновляет `refresh_token`.
        """
        refresh_token = request.COOKIES.get("refresh_token")
        print("🔄 Получили refresh_token из cookie:", refresh_token)

        if not refresh_token:
            raise AuthenticationFailed("Не авторизован", code="unauthorized")
        
        try:
            # Проверяем refresh_token
            token = RefreshToken(refresh_token)
            user_id = token.get("user_id")

            if not user_id:
                raise AuthenticationFailed("Refresh-токен не содержит user_id")
            
            user = User.objects.get(id=user_id)

            # ✅ Генерируем токены от имени пользователя
            new_refresh_token = RefreshToken.for_user(user)
            new_access_token = str(new_refresh_token.access_token)


           
            print("💬 Access:", new_access_token)
            print("💬 New refresh:", str(new_refresh_token))

            # ❌ старый refresh_token — в blacklist
            token.blacklist()

           # new_access_token["user_id"] = token["user_id"]

            # Генерируем новый `refresh_token`
            #new_refresh_token = str(RefreshToken())
           # print("💬 New refresh:", new_refresh_token)

       

            # Обновляем `refresh_token` в `httpOnly-cookie`
            response = Response({"access": new_access_token})
            response.set_cookie(
                key="refresh_token",
                value=str(new_refresh_token),
                httponly=True,  # ✅ Фронт не видит куку
                secure=settings.DEBUG is False,
                samesite="Lax",  # ✅ Защита от CSRF
                max_age=60 * 60 * 24 * 7,  # 7 дней
            )

            return response
        except Exception:
            raise AuthenticationFailed("Неверный токен", code="invalid_token")



        # # Добавляем refresh токен в `request.data`
        # request.data["refresh"] = refresh_token
        # return super().post(request, *args, **kwargs)

        

     

class LogoutView(APIView):
    """
    Удаляет refresh token из cookie и добавляет его в blacklist.
    """
    permission_classes = [IsAuthenticated]
    def post(self,request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response({"error": "Токен отсутствует"}, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"Полученный refresh_token: {refresh_token}")  # ✅ Логируем токен перед обработкой
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist() # Добавляем в черный список
        except Exception as e:
            print(f"Ошибка blacklisting: {str(e)}")  # ✅ Логируем ошибку на сервере
            return Response({"error": "Ошибка при диактивации токена"}, status=status.HTTP_400_BAD_REQUEST )
        
        # Удаляем refresh_token из cookie
        response = Response({"message": "Выход выполнен"})
        response.delete_cookie("refresh_token") # Удаляем `refresh_token`
        return response
   
    

class DownloadImageView(APIView):
    permission_classes = [IsAuthenticated]  # Только авторизованные пользователи

    def get(self, request, image_id):
        image = get_object_or_404(ImageModel, id=image_id)
        response = HttpResponse(image.file, content_type="image/jpeg")
        response["Content-Disposition"] = f'attachment; filename="{image.file.name}"'
        return response
    
class GetUserByUsernameView(APIView):
    permission_classes=[AllowAny]

    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
            return Response({"email": user.email}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)
        
class GetCurrentUserView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request):   
        print("👤 request.user:", request.user)
        print("🔐 headers:", request.headers.get('Authorization'))
        
        try:
            serializers = CurrentUserSerializer(request.user)
            return Response(serializers.data)
        except User.DoesNotExist:
            return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)
        

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
class CategoryView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    
class CustomCoursePagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100
    
class CoursesView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request, category_id):

        print("category_id@@@", category_id)
        print("request@@@", request)

        courses  = Course.objects.filter(category_id = category_id)

        

        if not courses.exists():
            return Response({"message":"Курсы не найдены для этой категории"}, status=status.HTTP_404_NOT_FOUND)
        
        paginator = CustomCoursePagination()
        paginates_courses = paginator.paginate_queryset(courses, request)


        serializer = CourseSerializer(paginates_courses, many=True)
        print("CoursesViewserializer@@@", serializer.data)
        return paginator.get_paginated_response(serializer.data)

class LessonsView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request, course_id):
        lessons = Lesson.objects.filter(course_id = course_id)
        if not lessons.exists():
            return Response ({"message":"Уроки не найдены для этой категории"}, status=status.HTTP_404_NOT_FOUND)
        
        paginator = CustomCoursePagination()
        paginates_lessons = paginator.paginate_queryset(lessons, request)
        serializer = LessonSerializer(paginates_lessons, many=True)
        print("LessonSerializerserializer@@@", serializer.data)
        return paginator.get_paginated_response(serializer.data)
    
class LessonById(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request, lesson_id):
        print("lesson_id_LessonById@@@" , lesson_id)
        lesson = Lesson.objects.filter(id=lesson_id).first()
        if not lesson:
            return Response({"message":"Урок не найден"}, status=status.HTTP_404_NOT_FOUND)
        serializer = LessonSerializer(lesson) 
        return Response(serializer.data)




