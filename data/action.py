import logging

import numpy

from config.models import Configuration
from data.exceptions import NoIntentError, NoActionIntentError
from turns.models import Sentence

logger = logging.getLogger('data')


class Action:
    def __init__(self, sentence: Sentence = None):
        """
        :param sentence: sentence to get the action from

        :raises NoIntentError: if the given sentence has no intent
        :raises NoActionIntentError: if the given sentence has an intent, that cannot be interpreted as action
        """
        self._action_vector = Action.vector_from_sentence(sentence)
        self._action_index = Configuration.get_active().action_index_for_name(sentence.intent.template.name)
        self.reward = float(sentence.reward)
        self.terminal = bool(sentence.terminal)

    def as_vector(self):
        return self._action_vector

    @property
    def intent_index(self):
        return self._action_index

    @property
    def name(self):
        return Configuration.action_intents[self._action_index]

    @staticmethod
    def vector_from_name(action_name: str):
        if not Configuration.get_active().is_action_intent(action_name):
            raise ValueError('There is no Action with name "{}"'.format(action_name))
        vector = numpy.zeros(Configuration.get_active().number_actions)
        vector[Configuration.get_active().action_index_for_name(action_name)] = 1.
        return vector

    @staticmethod
    def vector_from_sentence(sentence: Sentence):
        if sentence.intent is None:
            raise NoIntentError(sentence)
        if not Configuration.get_active().is_action_intent(sentence.intent.template.name):
            raise NoActionIntentError(sentence.intent, sentence)
        return Action.vector_from_name(sentence.intent.template.name)

    def __str__(self) -> str:
        return '<Action {}>'.format(Configuration.get_active().action_intents[self._action_index].name)

    def __format__(self, format_spec: str) -> str:
        return self.__str__()
