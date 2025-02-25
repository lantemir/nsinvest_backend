from django.urls import re_path
from main.consumers import ChatConsumer  # Импортируем WebSocket Consumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>\w+)/$", ChatConsumer.as_asgi()),
]