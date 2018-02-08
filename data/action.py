import logging

from keras.utils import to_categorical

from bot.config import ACTIONS, NUM_ACTIONS
from data.exceptions import NoIntentError, NoActionIntentError
from turns.models import Sentence

logger = logging.getLogger('data')


class Action:
    _action_vector = None
    reward = 0
    terminal = False

    def __init__(self, sentence: Sentence = None):
        """
        :param sentence: sentence to get the action from

        :raises NoIntentError: if the given sentence has no intent
        :raises NoActionIntentError: if the given sentence has an intent, that cannot be interpreted as action
        """
        self._action_vector = Action.vector_from_sentence(sentence)
        self._action_index = ACTIONS.index(sentence.intent.template.name)
        self.reward = float(sentence.reward)
        self.terminal = bool(sentence.terminal)

    def as_vector(self):
        return self._action_vector

    @property
    def index(self):
        return self._action_index

    @property
    def name(self):
        return ACTIONS[self._action_index]

    @staticmethod
    def vector_from_name(action_name: str):
        if action_name not in ACTIONS:
            raise ValueError('There is no Action with name "{}"'.format(action_name))
        return to_categorical(y=ACTIONS.index(action_name), num_classes=NUM_ACTIONS)[0]

    @staticmethod
    def vector_from_sentence(sentence: Sentence):
        if sentence.intent is None:
            raise NoIntentError(sentence)
        if sentence.intent.template.name not in ACTIONS:
            raise NoActionIntentError(sentence.intent, sentence)
        return Action.vector_from_name(sentence.intent.template.name)

    def __str__(self) -> str:
        return '<Action {}>'.format(ACTIONS[self._action_index])

    def __format__(self, format_spec: str) -> str:
        return self.__str__()
