import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.paginator import Paginator
from main.models import Message  # Импортируем модель сообщений
from asgiref.sync import sync_to_async
import base64
from django.core.files.base import ContentFile
from main.models import ChatRoom  # Импорт модели комнат
import asyncio

# Глобальный словарь активных пользователей
active_users = {}

class ChatConsumer(AsyncWebsocketConsumer):
    #Основная
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        user = self.scope["user"]  # Получаем пользователя

        # Присоединяемся к группе
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

         # Если пользователь аутентифицирован, добавляем его в список активных
        if user.is_authenticated:
            active_users[user.id] = user.username  # Сохраняем user_id → username

            # Отправляем событие "пользователь подключился"
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_status",
                    "user_id": user.id,
                    "username": user.username,                    
                    "status": "online",
                },
            )
            await self.send_active_users()

            await self.send_previous_messages()
    
    async def send_previous_messages(self, page=1):
        # Загружаем данные в list, чтобы избежать обращения к Django ORM в async-контексте
        messages = await sync_to_async(lambda: list(
            Message.objects.filter(room__name=self.room_name).order_by("-timestamp")
        ))()
        paginator = Paginator(messages, 20)  # 20 сообщений на страницу
        page_obj = paginator.get_page(page)

        async def serialize_message(msg):
            return {
                "user": await sync_to_async(lambda: msg.user.username)(),
                "message": msg.content,
                "image": msg.image.url if msg.image else None,
                "timestamp": msg.timestamp.isoformat(),
            }
        
        
        messages_data = []
        for msg in page_obj:
            serialized_msg = await serialize_message(msg)
            messages_data.append(serialized_msg)
        
        
        await self.send(text_data=json.dumps({"type": "chat_history", "messages": messages_data, "has_more": page_obj.has_previous()}))

    #Основная
    async def disconnect(self, close_code):
        """Обработчик отключения пользователя"""
        user = self.scope["user"]

        # Если пользователь аутентифицирован, убираем его из списка активных
        if user.is_authenticated and user.id in active_users:
            del active_users[user.id]


            # Отправляем событие "пользователь вышел"
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_status",
                    "user_id": user.id,
                    "username": user.username,
                    "status": "offline",
                },
            )
        # Покидаем группу
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def user_status(self, event):
        await self.send(text_data=json.dumps(event))

    async def send_active_users(self):
        """Отправляет актуальный список активных пользователей"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "active_users_list",
                "users": [{"id": user_id, "username": username} for user_id, username in active_users.items()],
            },
        )
    
    async def active_users_list(self, event):
        """Отправляет клиенту список активных пользователей"""
        await self.send(text_data=json.dumps(event))

    #Основная
    async def receive(self, text_data):
        data = json.loads(text_data)
        # message = data["message", ""]       
        message = data.get("message", "").strip()
        image_data = data.get("image", None)

        if not message and not image_data:  # Если ни текст, ни картинка не переданы, не отправляем
            return     

        image = None  # Добавляем это, чтобы избежать ошибки

        if image_data:
            format, imgstr = image_data.split(";base64,")  # Разбираем base64
            ext = format.split("/")[-1]  # Получаем расширение (jpg, png и т.д.)
            image = ContentFile(base64.b64decode(imgstr), name=f"chat_{self.room_name}_{self.scope['user'].id}.{ext}")
        else: 
            image: None

        chat_room, created = await sync_to_async(ChatRoom.objects.get_or_create)(name=self.room_name)  # Получаем объект комнаты

        

        message =await sync_to_async(Message.objects.create)(
            user=self.scope["user"],
            room=chat_room, #  Передаем объект, а не строку
            content=message,
            image=image,
        )

          

        message_data = {
            "user": message.user.username,
            "message": message.content,
            "image": message.image.url if message.image else None,
            "timestamp": message.timestamp.isoformat(),
        }

        if not message:  # Если пустое, не отправляем
            return        
        print(f"Получено сообщение: {message}")  # Для отладки

        user = self.scope["user"] # Получаем пользователя
        
        if user.is_authenticated:       

            # Отправляем сообщение в группу
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat_message", "message": message_data,}
            )

    async def chat_message(self, event):
        message = event["message"]
        

        # Отправляем сообщение обратно клиенту
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "message": message["message"],  #  Теперь это строка, а не объект!
            "username": message["user"],  #  Используем правильный ключ
            "image": message["image"],
            "timestamp": message["timestamp"],
        }))