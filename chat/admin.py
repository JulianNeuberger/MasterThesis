from django.contrib import admin

from chat.models import Message, Chat


@admin.register(Chat, Message)
class ChatAdmin(admin.ModelAdmin):
    pass
