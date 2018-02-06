import numpy
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
        self._action_index = ACTIONS.index(sentence.intent.template.name)
        self.reward = float(sentence.reward)
        self.terminal = bool(sentence.terminal)

    def as_vector(self):
        return self._action_vector

    def to_quality_vector(self, model, state_t0, context, state_t1):
        q_t1 = model.predict([state_t0], [context])[0]
        if self.terminal:
            q_t1[self._action_index] = self.reward
        else:
            context = context.push(state_t0, self)
            q_t2 = model.predict([state_t1], [context])[0]
            best_action_index = numpy.argmax(q_t2)
            q_t1[self._action_index] = self.reward + model.current_discount() * q_t2[best_action_index]
        return q_t1

    @staticmethod
    def _action_from_sentence(sentence: Sentence):
        if sentence.intent is None:
            raise NoIntentError(sentence)
        if sentence.intent.template.name not in ACTIONS:
            raise NoActionIntentError(sentence.intent, sentence)
        return to_categorical(y=ACTIONS.index(sentence.intent.template.name), num_classes=NUM_ACTIONS)[0]
