import logging
from threading import Thread
from time import sleep

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils import timezone

from bot.listener import BotListener
from chat.events import ChatMessageEvent
from config.models import Configuration
from turns.models import Sentence, Dialogue
from turns.util import update_all_for_single_sentence, update_user_profile_for_single_dialogue

logger = logging.getLogger('chat')


class ChatMessageListener:
    def __init__(self):
        self._terminator = TurnsTerminator()
        self._terminator.start()
        self._bot_user = User.objects.get(username='Chatbot')
        self._bot_listener = BotListener(self._bot_user)

    def on_message(self, event: ChatMessageEvent):
        logger.debug('Processing ChatMessageEvent in ChatMessageListener.')
        new_message = False
        try:
            sentence = Sentence.objects.get(raw_sentence=event.instance)
            ChatMessageListener._update_sentence_for_message(sentence, event)
            logger.debug('Message is already in database, updating reward')
        except ObjectDoesNotExist:
            sentence = self._get_sentence_for_message(event)
            new_message = True
            logger.debug('Message is not in database, creating new one')
        except MultipleObjectsReturned:
            logger.warning('Found multiple Sentence instances for one message instance! Will update the latest one...')
            sentence = Sentence.objects.filter(raw_sentence=event.instance).order_by('-said_on')[0]
            ChatMessageListener._update_sentence_for_message(sentence, event)
        if new_message:
            logger.info('Got new message, notifying chat bot endpoint.')
            self._bot_listener.on_message(sentence)

    def _get_sentence_for_message(self, event: ChatMessageEvent):
        sent_to = event.channel.initiator \
            if event.channel.initiator.username != self._bot_user.username \
            else event.channel.receiver
        assert sent_to != self._bot_user.username
        dialogue, _ = Dialogue.objects.get_or_create(with_user=sent_to.username)
        sentence = Sentence(value=event.value,
                            said_by=event.user.username,
                            said_in=dialogue,
                            reward=event.reward / 10,
                            raw_sentence=event.instance)
        sentence = update_all_for_single_sentence(sentence, save=True)
        update_user_profile_for_single_dialogue(sentence.said_in, False, True)
        sentence.refresh_from_db()
        return sentence

    @staticmethod
    def _update_sentence_for_message(sentence: Sentence, event: ChatMessageEvent):
        sentence.reward = event.reward / 10
        sentence.save()
        return sentence


class TurnsTerminator(Thread):
    """
    Periodically checks for terminated Dialogues, e.g. checks the last Sentence in a Dialogue
    and sets it to terminated, if there is no followup sentence for a while. Useful for
    training purposes, an episode of training memories could be generated as soon as we find a
    new terminated Dialogue.
    """

    def __init__(self):
        super().__init__()
        self.daemon = True

    def run(self):
        # TODO: why?
        sleep(5)
        logger.info("Started TurnsTerminator.")
        logger.info("TurnsTerminator checking for unterminated sentences.")
        while True:
            last_sentence_in_dialogues = Sentence.objects.raw(
                'SELECT * FROM turns_sentence GROUP BY said_in_id ORDER BY said_on DESC;')
            for sentence in last_sentence_in_dialogues:
                pause = timezone.now() - sentence.said_on
                pause = pause.seconds + pause.days * Configuration.get_active().seconds_per_day
                if pause >= Configuration.get_active().seconds_for_terminal and not sentence.terminal:
                    logger.info(
                        "Got no new sentence after {} seconds, {} has to be a terminal sentence".format(pause,
                                                                                                        sentence.value))
                    sentence.terminal = True
                    sentence.save()
            # Nyquist frequency, so we don't miss terminals
            sleep(Configuration.get_active().seconds_for_terminal / 2)
