import logging
import time

import numpy
import tensorflow as tf
from django.contrib.auth.models import User

from bot.bot import DeepMindBot
from chat.events import Singleton
from chat.models import Message, Chat
from config.models import Configuration
from content.responses import ResponseFactory
from data.context import Context
from data.state import State
from data.turn import Turn
from turns.models import Sentence, IntentTemplate, Intent, Dialogue
from turns.util import update_user_profile_for_single_dialogue

logger = logging.getLogger('bot')


class BotListener(metaclass=Singleton):
    def __init__(self):
        # TODO: FIXME: Get from database
        self._bot_user = User.objects.get(username='Chatbot')
        self.bot = DeepMindBot(bot_user=self._bot_user, load_dir='latest')
        self._graph = tf.get_default_graph()
        self._response_factories = {}
        self._init_factories()

    def change_bot(self, name):
        with self._graph.as_default():
            self.bot = DeepMindBot(bot_user=self._bot_user, load_dir=name)

    def on_message(self, sentence):
        assert isinstance(sentence, Sentence)
        logger.debug("Received notification on new message to bot, processing...")

        factory = self._get_and_update_factory(sentence)
        context = self._create_context_from_sentence(sentence)
        state = State(sentence)

        # mapping unknown_intent -> "Sorry didn't understand that" is hard coded, to avoid confusion
        if sentence.intent.template.name != Configuration.get_active().unknown_intent.name:
            action_name = self.bot.query({'state_input': numpy.array([state.as_vector()]),
                                          'context_input': numpy.array([context.as_matrix()])})
        else:
            action_name = Configuration.get_active().didnt_understand_intent.name

        human_user = User.objects.get(username=sentence.said_by)
        chat = Chat.objects.get(initiator=human_user, receiver=self._bot_user)

        sentence_value = factory.create_response(action_name)
        message = Message.objects.create(value=sentence_value, sent_by=self._bot_user, sent_in=chat)
        dialogue = sentence.said_in
        intent_template = IntentTemplate.objects.get(name=action_name)
        intent = Intent.objects.create(template=intent_template)
        response = Sentence.objects.create(value=sentence_value,
                                           said_in=dialogue,
                                           said_by=self._bot_user,
                                           raw_sentence=message,
                                           intent=intent,
                                           sentiment=0)
        update_user_profile_for_single_dialogue(response.said_in)
        response.refresh_from_db()

        logger.info('Responded to sentence {}(intent="{}") with action "{}". Done processing message!'.format(
            sentence,
            sentence.intent.template.name if sentence.intent is not None else 'Unknown intent',
            action_name
        ))

        self.bot.train()

    def _init_factories(self):
        logger.info('Initializing factories...')
        start = time.time()
        for name in Dialogue.objects.values_list('with_user', flat=True).distinct():
            self.update_factories(name)
        logger.info('Done initializing {} factories, took {:.4}s!'.format(
            len(self._response_factories.keys()),
            time.time() - start,
        ))

    def update_factories(self, name):
        if not self._response_factories.keys().__contains__(name):
            self._add_single_factory(name)

    def _add_single_factory(self, name):
        response_factory = ResponseFactory()
        for sentence in Sentence.objects.filter(said_by=name).order_by('said_on'):
            if sentence.intent is not None:
                response_factory.update(sentence.intent)
        self._response_factories[name] = response_factory

    def _get_and_update_factory(self, sentence):
        if not self._response_factories.keys().__contains__(sentence.said_by):
            self.update_factories(sentence.said_by)
        factory = self._response_factories.get(sentence.said_by, None)
        factory.update(sentence.intent)
        return factory

    def _create_context_from_sentence(self, sentence):
        sentences_needed = Configuration.get_active().context_length * 2  # each context needs 2 sentences to be built
        sentence_query = Sentence.objects.filter(said_in=sentence.said_in).order_by('-said_on')
        sentences_available = sentence_query.count()
        num_sentences = min(sentences_needed, sentences_available)
        sentences = sentence_query[:num_sentences]
        sentences = list(reversed(sentences))
        single_sentence = None
        while single_sentence is None or single_sentence.said_by == self._bot_user:
            # we need to find the first user made sentence
            try:
                single_sentence = sentences.pop()
            except IndexError:
                # there never was a user-said sentence... skip the response!
                return
        while len(sentences) > 0 and sentences[0].said_by == self._bot_user:
            # the first sentence needs to be user-said
            sentences.pop(0)
        logger.debug('Reacting to sentence {}'.format(single_sentence))
        logger.debug('Have these sentences as context: {}'.format(sentences))
        turns = Turn.sentences_to_turns(sentences, self._bot_user)
        context = Context.get_single_context(turns, Configuration.get_active().context_length)
        return context
