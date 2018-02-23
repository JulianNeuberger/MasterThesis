from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer

from chat.models import Message, Chat


class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        exclude = ('user_permissions',)


class ChatSerializer(ModelSerializer):
    class Meta:
        model = Chat
        fields = '__all__'
