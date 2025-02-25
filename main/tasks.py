from datetime import timedelta
from celery import shared_task
from django.utils.timezone import now
from .models import EmailVerificationCode
from django.core.mail import send_mail
from smtplib import SMTPException


@shared_task
def delete_expired_verification_codes():
    """
    Удаляет коды, которым больше 10 минут
    """

    expiration_time = now() - timedelta(minutes=10)
    deleted_count, _ = EmailVerificationCode.objects.filter(created_at__lt=expiration_time).delete()
    print(f"✅ Удалено {deleted_count} устаревших кодов подтверждения")

@shared_task
def send_verification_email(email, verification_code):
    """
    Асинхронная отправка email с кодом подтверждения через Celery
    """
    try:
        send_mail(
                    "Код подтверждения",
                    f"Ваш код подтверждения: {verification_code}",
                    "lan888developer@gmail.com",  # Должен совпадать с EMAIL_HOST_USER
                    [email],
                    fail_silently=False,
                )
    
    except SMTPException as e:
        return f"Ошибка при отправке email на {email}: {str(e)}"