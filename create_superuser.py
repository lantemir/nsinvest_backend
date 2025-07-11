import os
import django
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.getenv('DJANGO_SUPERUSER_USERNAME')
email = os.getenv('DJANGO_SUPERUSER_EMAIL')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

if not username or not email or not password:
    logger.warning("⚠️  Не заданы переменные окружения DJANGO_SUPERUSER_USERNAME, EMAIL или PASSWORD.")
else:
    if User.objects.filter(username=username).exists():
        logger.info(f"✅ Суперпользователь '{username}' уже существует.")
    else:
        try:
            User.objects.create_superuser(username=username, email=email, password=password)
            logger.info(f"✅ Суперпользователь '{username}' успешно создан.")
        except Exception as e:
            logger.error(f"❌ Ошибка при создании суперпользователя: {e}")
