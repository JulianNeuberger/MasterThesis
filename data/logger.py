import logging

from django.conf import settings

from events.listener import SlackEventsListener, BaseMessageEvent
from turns.models import Dialogue, Sentence

DIALOG_FLOW_TOKEN = getattr(settings, 'DIALOG_FLOW_TOKEN', None)
SLACK_VERIFICATION_TOKEN = getattr(settings, 'SLACK_VERIFICATION_TOKEN', None)
SLACK_BOT_USER_TOKEN = getattr(settings, 'SLACK_BOT_USER_TOKEN', None)

logger = logging.getLogger('data')


class Logger(SlackEventsListener):
    def on_message(self, event: BaseMessageEvent):
        super().on_message(event)
        dialogue, created = Dialogue.objects.get_or_create(with_user=event.channel)
        try:
            last_sentence = Sentence.objects.filter(said_in=dialogue).latest(field_name='said_on')
        except Sentence.DoesNotExist:
            last_sentence = None
        if last_sentence is None or last_sentence.said_by != event.username:
            # only allow 1-1 turns
            sentence = Sentence(value=event.message, said_by=event.username, said_in=dialogue)
            sentence.save()
            logger.info('Saved new sentence "{}" said in dialogue "{}"'.format(sentence, dialogue))
        else:
            # TODO: shouldn't this be logged, too and just filtered out while pre processing?
            logger.info('Sentence is from same person as the one before, not saving it!')
