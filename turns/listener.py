import logging
from threading import Thread
from time import sleep

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils import timezone

from bot.config import SECONDS_FOR_TERMINAL, SECONDS_PER_DAY, SENTENCE_BUFFER_SIZE
from bot.listener import BotListener
from chat.events import ChatMessageEvent
from turns.models import Sentence, Dialogue
from turns.util import update_all_for_single_sentence, update_user_profile_for_single_dialogue

logger = logging.getLogger('chat')


class ChatMessageListener:
    def __init__(self):
        self._terminator = TurnsTerminator()
        self._terminator.start()
        bot_user = User.objects.get(username='Chatbot')
        self._bot_listener = BotListener(bot_user=bot_user)

    def on_message(self, event: ChatMessageEvent):
        logger.debug('Processing ChatMessageEvent in ChatMessageListener.')
        new_message = False
        try:
            sentence = Sentence.objects.get(raw_sentence=event.instance)
            ChatMessageListener._update_sentence_for_message(sentence, event)
            logger.debug('Message is already in database, updating reward')
        except ObjectDoesNotExist:
            sentence = ChatMessageListener._get_sentence_for_message(event)
            new_message = True
            logger.debug('Message is not in database, creating new one')
        except MultipleObjectsReturned:
            logger.warning('Found multiple Sentence instances for one message instance! Will update the latest one...')
            sentence = Sentence.objects.filter(raw_sentence=event.instance).order_by('-said_on')[0]
            ChatMessageListener._update_sentence_for_message(sentence, event)
        if new_message:
            logger.info('Got new message, notifying chat bot endpoint.')
            self._bot_listener.on_message(sentence)

    @staticmethod
    def _update_sentence_for_message(sentence: Sentence, event: ChatMessageEvent):
        sentence.reward = event.reward
        sentence.save()
        return sentence

    @staticmethod
    def _get_sentence_for_message(event: ChatMessageEvent):
        sent_to = event.channel.initiator \
            if event.channel.initiator.username != event.user.username \
            else event.channel.receiver
        dialogue, _ = Dialogue.objects.get_or_create(with_user=sent_to.username)
        sentence = Sentence(value=event.value,
                            said_by=event.user.username,
                            said_in=dialogue,
                            raw_sentence=event.instance)
        sentence = update_all_for_single_sentence(sentence, save=True)
        update_user_profile_for_single_dialogue(sentence.said_in, False, True)
        sentence.refresh_from_db()
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

                    sentences = Sentence.objects.filter(used_in_training=False, said_in=sentence.said_in)
                    num_sentences = len(sentences)
                    if num_sentences >= SENTENCE_BUFFER_SIZE:
                        logger.info(
                            'There are {} sentences not used for training, notifying bot to train on them.'.format(
                                num_sentences
                            ))
                        bot_user = User.objects.get(username='Chatbot')
                        BotListener(bot_user).on_batch(sentences)
                    else:
                        logger.debug(
                            'Not enough unused sentences for one episode, cannot train!')
