from django.contrib import admin


from .models import InvestmentProject, ChatRoom, Message, EmailVerificationCode, Profile, Category, Course, Lesson

# Register your models here.
admin.site.register(InvestmentProject)
admin.site.register(ChatRoom)
admin.site.register(Message)
admin.site.register(EmailVerificationCode)

admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Course)
admin.site.register(Lesson)

