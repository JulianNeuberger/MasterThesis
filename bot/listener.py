import logging

import numpy
from django.contrib.auth.models import User

from bot.bot import QueryableModel
from bot.config import CONTEXT_LENGTH, ACTIONS, ACTION_SENTENCES
from chat.models import Message, Chat
from data.context import Context
from data.state import State
from data.turn import Turn
from turns.models import Sentence
from turns.util import update_all_for_single_sentence

logger = logging.getLogger('bot')


class BotListener:
    def __init__(self, bot_user: User):
        self._model = QueryableModel()
        self._user = bot_user

    def notify(self, sentence):
        assert isinstance(sentence, Sentence)

        logger.debug("Recieved notification on new message to bot, processing...")

        sentences = Sentence.objects.order_by('-said_on').filter(said_in=sentence.said_in)[:CONTEXT_LENGTH * 2]
        sentences = list(reversed(sentences))
        single_sentence = sentences[-1]
        sentences = sentences[:-1]
        logger.debug('Have these sentences as context: {}'.format(sentences))
        logger.debug('Reacting to sentence "{}"'.format(single_sentence))
        turns = Turn.sentences_to_turns(sentences)
        logger.debug('These Turns are generated from contexts: {}'.format(turns))
        context = Context.get_single_context(turns, CONTEXT_LENGTH)
        logger.debug('Successfully created context "{}" from turns'.format(context))

        state = State(sentence)
        logger.debug('Querying the model with state {} and context {}'.format(state, context))
        action = self._model.query([state], [context])[0]
        logger.debug('Done querying! Raw result is: {}'.format(action))
        action = ACTIONS[numpy.argmax(action)]
        logger.debug('This results in action with name {}'.format(action))

        human_user = User.objects.get(username=sentence.said_by)
        chat = Chat.objects.get(initiator=human_user, receiver=self._user)

        logger.debug('Will send the action to user "{}" in chat "{}"'.format(human_user, chat))

        sentence_value = ACTION_SENTENCES[action]
        message = Message.objects.create(value=sentence_value, sent_by=self._user, sent_in=chat)
        dialogue = sentence.said_in
        sentence = Sentence.objects.create(value=sentence_value, said_in=dialogue)
        sentence = update_all_for_single_sentence(sentence, True)

        logger.debug('Sending message "{}"'.format(message))
        logger.info('Responded to sentence "{}"({}) with action "{}". Done processing message!'.format(
            sentence,
            sentence.intent.template.name if sentence.intent is not None else 'Unknown intent',
            action
        ))