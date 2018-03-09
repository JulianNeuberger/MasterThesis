# Create your views here.
import json
import logging
from datetime import datetime
from json import JSONDecodeError

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets, generics

from chat.events import ListenerManager, ChatMessageEvent
from chat.models import Message, Chat, Settings
from chat.serializers import MessageSerializer, UserSerializer, ChatSerializer

logger = logging.getLogger('chat')


@login_required
@ensure_csrf_cookie
def single_chat(request, chat_id):
    settings, _ = Settings.objects.get_or_create(for_user=request.user)
    settings.visits = F('visits') + 1
    settings.save()
    settings.refresh_from_db()
    logger.debug('Got a visit from {}, this is the {}th visit.'.format(
        request.user.username,
        settings.visits
    ))
    context = {
        'user_id': request.user.id,
        'chat_id': chat_id,
        'settings': settings.visits
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
@require_http_methods(['GET'])
def start_bot_chat(request):
    # FIXME: Dirty hack, store default chatbot user in db
    bot_user = User.objects.get(username='Chatbot')
    assert bot_user is not None, 'We need some kind of bot user for this to work'
    chat = Chat.objects.create(initiator=request.user, receiver=bot_user,
                               name='bot_chat_{}_with_{}'.format(datetime.now(), request.user.username))
    return redirect('single', chat_id=chat.id)


@login_required
@require_http_methods(['POST'])
def show_tutorial(request):
    try:
        data = request.body.decode('utf-8')
        request_data = json.loads(data)
        show = request_data['show']
    except KeyError:
        return HttpResponseBadRequest('Missing parameter show.')
    except JSONDecodeError:
        return HttpResponseBadRequest('Body of request needs to be valid json.')
    user_settings = Settings.objects.get(for_user=request.user)
    user_settings.show_tutorial = show
    user_settings.save()
    return JsonResponse({
        'success': True,
        'errors': []
    })


class ChatMessageList(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        chat_id = self.request.query_params.get('sent_in_id', None)
        query_set = Message.objects.all()
        if chat_id is not None:
            query_set = query_set.filter(sent_in_id=chat_id)
        last_message_time = self.request.query_params.get('sent_on__gt', None)
        if last_message_time is not None:
            query_set = query_set.filter(sent_on__gt=last_message_time)
        return query_set


class MessageViewSet(ChatMessageList, viewsets.ModelViewSet):
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

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        max_messages = 20
        num_messages = queryset.count()
        if num_messages > max_messages:
            queryset = queryset[num_messages - max_messages: num_messages]
        return queryset


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
