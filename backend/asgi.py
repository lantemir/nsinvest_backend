

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
from backend.routing import websocket_urlpatterns
from backend.chat.middleware import JWTAuthMiddleware

# application = get_asgi_application()

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),  # Обычные HTTP-запросы
#     "websocket": JWTAuthMiddleware(
#         URLRouter(websocket_urlpatterns)  # WebSocket-маршруты
#     ),
# })

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            URLRouter(websocket_urlpatterns)
        )
    ),
})