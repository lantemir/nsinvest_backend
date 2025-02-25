from django.urls import path

from .views import CustomTokenRefreshView, RegisterView, LogoutView, CustomTokenObtainPairView, DownloadImageView, VerifyEmailView, ResendVerificationCodeView, GetUserByUsernameView


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
    path("download-image/<int:image_id>/", DownloadImageView.as_view(), name="download_image"),
]