import logging

from events.listener import BaseMessageEvent

logger = logging.getLogger('chat')


class CustomChatEventsListener:
    def notify(self, event: BaseMessageEvent):
        assert isinstance(event, BaseMessageEvent)
        logger.info('Got message "{}"'.format(event.message))
