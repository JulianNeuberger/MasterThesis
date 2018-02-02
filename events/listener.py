import logging

from events.util import Singleton

logger = logging.getLogger('events')


class BaseChatEvent:
    def __init__(self, user_name, channel):
        self.username = user_name
        self.channel = channel


class BaseMessageEvent(BaseChatEvent):
    def __init__(self, user_name, channel, message):
        """
        :param user_name: User that send the message
        :param channel: Channel name, message was send in
        :param message: the actual message in plain text
        """
        super().__init__(user_name, channel)
        self.message = message


class SlackEventsListener:
    def __init__(self):
        self._event_function_mapping = {
            BaseMessageEvent: self.on_message
        }

    def on_message(self, event: BaseMessageEvent):
        logger.debug("Got a new message.")

    def notify(self, event):
        self._function_for_event(event)(event)

    def _function_for_event(self, event):
        return self._event_function_mapping[type(event)]


class EventManager:
    def __init__(self):
        self._listeners = []

    def register_listener(self, listener):
        assert hasattr(listener, 'notify'), \
            'Listeners registered on {} need at least the notify(self, event) method.'.format(
                self.__class__.__name__
            )
        logger.debug("New listener '{}' in manager '{}'!".format(listener.__class__.__name__, self))
        self._listeners.append(listener)

    def unregister_listener(self, listener):
        self._listeners.remove(listener)

    def notify_listeners(self, event):
        for listener in self._listeners:
            logger.debug('notified listener {} for manager {}'.format(listener, self))
            listener.notify(event)


class SlackEventManager(EventManager, metaclass=Singleton):
    pass


class CustomChatEventManager(EventManager, metaclass=Singleton):
    pass
