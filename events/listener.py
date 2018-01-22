import logging

from events.util import Singleton

logger = logging.getLogger('events')


class SlackBaseEvent:
    def __init__(self, user_name, channel):
        self.user_name = user_name
        self.channel = channel


class SlackMessageEvent(SlackBaseEvent):
    def __init__(self, user_name, channel, message):
        super().__init__(user_name, channel)
        self.message = message


class SlackEventsListener:
    def __init__(self):
        self._event_function_mapping = {
            SlackMessageEvent: self.on_message
        }

    def on_message(self, event: SlackMessageEvent):
        logger.debug("Got a new message.")

    def notify(self, event):
        self._function_for_event(event)(event)

    def _function_for_event(self, event):
        return self._event_function_mapping[type(event)]


class EventManager:
    def __init__(self):
        self._listeners = []

    def register_listener(self, listener: SlackEventsListener):
        logger.debug("New listener '{}' in manager '{}'!".format(listener.__class__, self))
        self._listeners.append(listener)

    def unregister_listener(self, listener: SlackEventsListener):
        self._listeners.remove(listener)

    def notify_listeners(self, event):
        for listener in self._listeners:
            logger.debug('notified listener {} for manager {}'.format(listener, self))
            listener.notify(event)


class SlackEventManager(EventManager, metaclass=Singleton):
    pass


class CustomChatEventManager(EventManager, metaclass=Singleton):
    pass
