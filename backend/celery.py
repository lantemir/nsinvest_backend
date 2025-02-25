import os
from celery import Celery
from celery.schedules import crontab

# Загружаем настройки Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# Создаем Celery-приложение
celery_app = Celery("backend")

# Загружаем настройки Celery из settings.py
celery_app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматически обнаруживаем задачи в apps
celery_app.autodiscover_tasks()

celery_app.conf.beat_schedule = {
    "delete_expired_codes_every_10_minutes": {
        "task": "main.tasks.delete_expired_verification_codes",
        "schedule": crontab(minute="*/10"),  # Запуск каждые 10 минут
    },
}