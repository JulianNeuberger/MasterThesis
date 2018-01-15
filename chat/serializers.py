from django.contrib.auth.models import User
from rest_framework.serializers import HyperlinkedModelSerializer

from chat.models import Message, Chat


class MessageSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'


class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        exclude = ('user_permissions',)


class ChatSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Chat
        fields = '__all__'
