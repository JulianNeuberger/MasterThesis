import logging

import numpy
from django.contrib.auth.models import User

from bot.bot import QueryableModel
from bot.config import CONTEXT_LENGTH, ACTIONS, ACTION_SENTENCES
from chat.events import Singleton
from chat.models import Message, Chat
from data.context import Context
from data.state import State
from data.turn import Turn
from turns.models import Sentence, IntentTemplate, Intent
from turns.transition import Transition
from turns.util import update_user_profile_for_single_dialogue

logger = logging.getLogger('bot')


class BotListener(metaclass=Singleton):
    def __init__(self, bot_user: User):
        self._model = QueryableModel()
        self._user = bot_user

    def on_message(self, sentence):
        assert isinstance(sentence, Sentence)

        logger.debug("Received notification on new message to bot, processing...")

        sentences_needed = CONTEXT_LENGTH * 2  # each context needs 2 sentences to be built
        sentence_query = Sentence.objects.order_by('-said_on').filter(said_in=sentence.said_in)
        logger.debug('Considering sentences "{}"'.format(sentence_query.all()))
        sentences_available = sentence_query.count()
        logger.debug('There are {} sentences, that can be used as context'.format(sentences_available))
        num_sentences = min(sentences_needed, sentences_available)
        logger.debug('Using {} sentences as context'.format(num_sentences))
        sentences = sentence_query[:num_sentences]
        logger.debug('These sentences are "{}"'.format(sentences))
        sentences = list(reversed(sentences))
        logger.debug('Reversing them yield the raw turns "{}"'.format(sentences))
        single_sentence = None
        while single_sentence is None or single_sentence.said_by == self._user:
            # we need to find the first user made sentence
            try:
                single_sentence = sentences.pop()
            except IndexError:
                # there never was a user-said sentence... skip the response!
                return
        while len(sentences) > 0 and sentences[0].said_by == self._user:
            # the first sentence needs to be user-said
            sentences.pop(0)
        logger.debug('Have these sentences as context: {}'.format(sentences))
        logger.debug('Reacting to sentence "{}"'.format(single_sentence))
        turns = Turn.sentences_to_turns(sentences, self._user)
        logger.debug('These Turns are generated from sentences: {}'.format(turns))
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
        intent_template = IntentTemplate.objects.get(name=action)
        intent = Intent.objects.create(template=intent_template)
        response = Sentence.objects.create(value=sentence_value,
                                           said_in=dialogue,
                                           said_by=self._user,
                                           raw_sentence=message,
                                           intent=intent,
                                           sentiment=0)
        update_user_profile_for_single_dialogue(response.said_in)
        response.refresh_from_db()

        logger.debug('Sending message "{}"'.format(message))
        logger.info('Responded to sentence "{}"({}) with action "{}". Done processing message!'.format(
            sentence,
            sentence.intent.template.name if sentence.intent is not None else 'Unknown intent',
            action
        ))

    def on_reward(self, sentence):
        pass

    def on_batch(self, sentences):
        logger.info("Received signal to online train on a batch of sentences.")
        logger.info("Sentences are {}".format(sentences))

        turns = Turn.sentences_to_turns(sentences, self._user)
        transitions = Transition.all_transitions_from_turns(turns, CONTEXT_LENGTH)
        self._model.train(transitions)

        logger.info("Training successful, setting {} used sentences to 'used in training'...".format(
            len(sentences)
        ))
        for sentence in sentences:
            sentence.used_in_training = True
            sentence.save()
