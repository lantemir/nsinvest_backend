from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model

User = get_user_model()


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)

        token = params.get("token", [None])[0]  # Берем токен из URL

        scope["user"] = AnonymousUser()  # По умолчанию аноним

        if token:
            try:
                access_token = AccessToken(token)
                user = await self.get_user(access_token["user_id"])
                scope["user"] = user
            except Exception as e:
                print(f"JWT WebSocket Auth Error: {e}")

        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return AnonymousUser()