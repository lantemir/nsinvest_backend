from django.urls import path

from .views import (CustomTokenRefreshView, RegisterView, LogoutView, 
                    CustomTokenObtainPairView, DownloadImageView, VerifyEmailView, 
                    ResendVerificationCodeView, GetUserByUsernameView, GetCurrentUserView,
                    CategoryView, ProfileView, CoursesView, LessonsView, LessonById)


urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    # path("chatrooms/", ChatRoomListCreateView.as_view(), name="chatroom-list"),
    # path("messages/", MessageListCreateView.as_view(), name="message-list"),
    path("auth/resend-verification-code/", ResendVerificationCodeView.as_view(), name="resend-verification-code"),
    path("auth/get-user-by-username/<str:username>/", GetUserByUsernameView.as_view(), name="get_user_by_username"),
    path("auth/me/", GetCurrentUserView.as_view(), name="get_current_user"),
    path("download-image/<int:image_id>/", DownloadImageView.as_view(), name="download_image"),
    path("auth/profile/", ProfileView.as_view(), name="user-profile"),
    path("categories/", CategoryView.as_view(), name="category"),
    path("courses/by-category/<int:category_id>/", CoursesView.as_view(), name="courses_category"),
    path("lesson/by-course/<int:course_id>/", LessonsView.as_view(), name="lesson_category"),
    path("lesson/by-id/<int:lesson_id>/", LessonById.as_view(), name="lesson_id" ), 
]