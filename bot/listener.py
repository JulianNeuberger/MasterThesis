import logging

from bot.model import QueryableModel
from events.listener import BaseMessageEvent
from turns.models import Sentence, Dialogue

logger = logging.getLogger('bot')


class BotListener:
    def __init__(self):
        self.model = QueryableModel()

    def notify(self, event: BaseMessageEvent):
        assert isinstance(event, BaseMessageEvent)
        sentence = Sentence.objects.filter(said_by=event.user_name).order_by('said_on').last()
        assert sentence is not None
        action = self.model.query()
        logger.info('Bot replying to message "{}" with action "{}"'.format(
            event.message,

        ))
        dialogue, _ = Dialogue.objects.get_or_create(with_user=event.channel)
        sentence = Sentence(value=event.message, said_by=event.user_name, said_in=dialogue)
        sentence.save()
