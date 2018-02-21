import logging

import numpy
from django.contrib.auth.models import User

from bot.bot import DeepMindModel
from bot.config import CONTEXT_LENGTH, ACTION_SENTENCES
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
        self._user = bot_user
        self._model = DeepMindModel(bot_user=self._user)

    def on_message(self, sentence):
        assert isinstance(sentence, Sentence)

        logger.debug("Received notification on new message to bot, processing...")

        sentences_needed = CONTEXT_LENGTH * 2  # each context needs 2 sentences to be built
        sentence_query = Sentence.objects.order_by('-said_on').filter(said_in=sentence.said_in)
        sentences_available = sentence_query.count()
        num_sentences = min(sentences_needed, sentences_available)
        sentences = sentence_query[:num_sentences]
        sentences = list(reversed(sentences))
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
        logger.debug('Reacting to sentence "{}"'.format(single_sentence))
        logger.debug('Have these sentences as context: {}'.format(sentences))
        turns = Turn.sentences_to_turns(sentences, self._user)
        context = Context.get_single_context(turns, CONTEXT_LENGTH)
        state = State(sentence)
        action_name = self._model.query({'state_input': numpy.array([state.as_vector()]),
                                         'context_input': numpy.array([context.as_matrix()])})
        human_user = User.objects.get(username=sentence.said_by)
        chat = Chat.objects.get(initiator=human_user, receiver=self._user)

        sentence_value = ACTION_SENTENCES[action_name]
        message = Message.objects.create(value=sentence_value, sent_by=self._user, sent_in=chat)
        dialogue = sentence.said_in
        intent_template = IntentTemplate.objects.get(name=action_name)
        intent = Intent.objects.create(template=intent_template)
        response = Sentence.objects.create(value=sentence_value,
                                           said_in=dialogue,
                                           said_by=self._user,
                                           raw_sentence=message,
                                           intent=intent,
                                           sentiment=0)
        update_user_profile_for_single_dialogue(response.said_in)
        response.refresh_from_db()

        logger.info('Responded to sentence "{}"({}) with action "{}". Done processing message!'.format(
            sentence,
            sentence.intent.template.name if sentence.intent is not None else 'Unknown intent',
            action_name
        ))

        self._model.train()
