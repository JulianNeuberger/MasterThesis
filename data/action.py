from keras.utils import to_categorical

from bot.config import ACTIONS, NUM_ACTIONS
from data.exceptions import NoIntentError, NoActionIntentError
from turns.models import Sentence


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
        self._action_vector = Action._action_from_sentence(sentence)
        self.reward = float(sentence.reward)
        self.terminal = bool(sentence.terminal)

    def as_vector(self):
        return self._action_vector

    @staticmethod
    def _action_from_sentence(sentence: Sentence):
        if sentence.intent is None:
            raise NoIntentError(sentence)
        if sentence.intent.template.name not in ACTIONS:
            raise NoActionIntentError(sentence.intent)
        return to_categorical(y=ACTIONS.index(sentence.intent.template.name), num_classes=NUM_ACTIONS)[0]
