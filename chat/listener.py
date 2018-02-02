import logging
from threading import Thread
from time import sleep

from django.contrib.auth.models import User
from django.utils import timezone

from bot.config import SECONDS_FOR_TERMINAL, SECONDS_PER_DAY
from bot.listener import BotListener
from events.listener import BaseMessageEvent
from turns.models import Sentence, Dialogue
from turns.util import update_all_for_single_sentence

logger = logging.getLogger('chat')


class CustomChatEventsListener:
    def __init__(self):
        self._terminator = TurnsTerminator()
        self._terminator.start()
        bot_user = User.objects.get(username='Chatbot')
        self._bot_listener = BotListener(bot_user=bot_user)

    def notify(self, event: BaseMessageEvent):
        assert isinstance(event, BaseMessageEvent)
        sent_to = event.channel.initiator \
            if event.channel.initiator.username != event.username \
            else event.channel.receiver
        logger.info('Got message "{}" from "{}" to "{}"'.format(event.message, event.username, sent_to.username))
        dialogue, _ = Dialogue.objects.get_or_create(with_user=sent_to.username)
        sentence = Sentence(value=event.message, said_by=event.username, said_in=dialogue)
        sentence = update_all_for_single_sentence(sentence, save=True)
        logger.info('Notified chat bot endpoint.')
        self._bot_listener.notify(sentence)


class TurnsTerminator(Thread):
    def run(self):
        logger.info("Started TurnsTerminator.")
        while True:
            logger.info("TurnsTerminator checking for unterminated sentences.")
            sleep(SECONDS_FOR_TERMINAL)
            last_sentence_in_dialogues = Sentence.objects.raw(
                'SELECT * FROM turns_sentence GROUP BY said_in_id ORDER BY said_on DESC;')
            for sentence in last_sentence_in_dialogues:
                logger.debug('Considering sentence "{}".'.format(sentence))
                pause = timezone.now() - sentence.said_on
                pause = pause.seconds + pause.days * SECONDS_PER_DAY
                logger.debug("There is a pause of {} seconds!".format(pause))
                if pause >= SECONDS_FOR_TERMINAL:
                    logger.info(
                        "Got no new sentence after {} seconds, this has to be a terminal sentence".format(pause))
                    sentence.terminal = True
                    sentence.save()
