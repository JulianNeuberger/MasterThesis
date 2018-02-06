# Create your views here.
import logging
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import viewsets

from chat.events import ListenerManager, ChatMessageEvent
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


@login_required
@ensure_csrf_cookie
def index(request):
    logger.debug('Showing index for user "{}"'.format(request.user))
    bot_user = User.objects.get(username='Chatbot')
    assert bot_user is not None, 'We need some kind of bot user for this to work'
    try:
        chat = Chat.objects.get(initiator=request.user, receiver=bot_user)
    except ObjectDoesNotExist:
        chat = Chat.objects.create(initiator=request.user, receiver=bot_user,
                                   name='bot_chat_{}_with_{}'.format(datetime.now(), request.user.username))
    return redirect('single', chat_id=chat.id)


@login_required
def start_bot_chat(request):
    assert request.user is not None, 'login is required to start chat with bot'
    # FIXME: Dirty hack, maybe the chat should assume receiver is the bot?
    bot_user = User.objects.get(username='Chatbot')
    assert bot_user is not None, 'We need some kind of bot user for this to work'
    chat = Chat.objects.create(initiator=request.user, receiver=bot_user,
                               name='bot_chat_{}_with_{}'.format(datetime.now(), request.user.username))
    return redirect('single', chat_id=chat.id)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    event_manager = ListenerManager()

    def perform_update(self, serializer):
        logger.debug('Got updated message, notifying all.')
        instance = serializer.save()
        self.event_manager.notify_all(
            ChatMessageEvent(message_instance=instance)
        )
        return instance

    def perform_create(self, serializer):
        logger.debug('Got new message, notifying all.')
        instance = serializer.save()
        self.event_manager.notify_all(
            ChatMessageEvent(message_instance=instance)
        )
        return instance


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
