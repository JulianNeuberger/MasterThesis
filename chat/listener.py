import logging

from events.listener import BaseMessageEvent
from turns.models import Sentence, Dialogue

logger = logging.getLogger('chat')


class CustomChatEventsListener:
    def notify(self, event: BaseMessageEvent):
        assert isinstance(event, BaseMessageEvent)
        logger.info('Got message "{}"'.format(event.message))
        dialogue, _ = Dialogue.objects.get_or_create(with_user=event.channel)
        sentence = Sentence(value=event.message, said_by=event.user_name, said_in=dialogue)
        sentence.save()
