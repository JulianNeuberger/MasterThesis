# Create your views here.
import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.template.response import TemplateResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import viewsets

from chat.models import Message, Chat
from chat.serializers import MessageSerializer, UserSerializer, ChatSerializer

logger = logging.getLogger('chat')


@login_required
@ensure_csrf_cookie
def single_chat(request, chat_id):
    serializing_context = {'request': request}
    user_serializer = UserSerializer(request.user, context=serializing_context)
    chat = Chat.objects.get(id=chat_id)
    chat_serializer = ChatSerializer(chat, context=serializing_context)
    context = {
        'user_url': user_serializer.data['url'],
        'chat_url': chat_serializer.data['url']
    }
    return TemplateResponse(request=request, template='chat/single.html', context=context)


class RestEndPoint:
    def __init__(self):
        pass




@login_required
@ensure_csrf_cookie
def index(request):
    logger.debug('Showing index for user "{}"'.format(request.user))
    context = {'chats': Chat.objects.filter(Q(initiator=request.user) | Q(receiver=request.user)).all()}
    return TemplateResponse(request=request, template='chat/index.html', context=context)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def create(self, request, *args, **kwargs):
        ret = super().create(request, *args, **kwargs)
        logger.debug('Added a message successfully')
        return ret


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
