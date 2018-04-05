import logging
from enum import Enum

from chat.models import Message

logger = logging.getLogger('chat')


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class ChatMessageEventType(Enum):
    CREATED = 1
    RATED = 2


class ChatMessageEvent:
    def __init__(self, message_instance: Message, event_type=ChatMessageEventType.CREATED):
        self.instance = message_instance
        self.value = message_instance.value
        self.user = message_instance.sent_by
        self.channel = message_instance.sent_in
        self.reward = message_instance.reward
        self.event_type = event_type


class ListenerManager(metaclass=Singleton):
    def __init__(self):
        self._managed_listeners = []

    def add_listener(self, listener):
        assert hasattr(listener, 'on_message'), 'A proper listener needs at least the on_message method'
        self._managed_listeners.append(listener)
        logger.info('Now managing chat message listener "{}"'.format(listener))

    def notify_all(self, event):
        logger.info('Notifying {} listeners about event "{}"'.format(
            len(self._managed_listeners),
            event.__class__.__name__
        ))
        for listener in self._managed_listeners:
            listener.on_message(event)
