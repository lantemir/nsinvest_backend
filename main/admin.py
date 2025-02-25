from django.contrib import admin

from .models import InvestmentProject, ChatRoom, Message, EmailVerificationCode

# Register your models here.
admin.site.register(InvestmentProject)
admin.site.register(ChatRoom)
admin.site.register(Message)
admin.site.register(EmailVerificationCode)

