import logging

import numpy
from keras.utils import to_categorical
from numpy.core.multiarray import ndarray

from bot.config import INTENTS, NUM_INTENTS
from turns.models import Sentence, UserProfile

logger = logging.getLogger('data')


class State:
    intent_vector = None
    sentiment = 0
    user_profile_vector = None

    def __init__(self, sentence: Sentence = None):
        """
        creates a new state, if sentence is given, the fields will be populated with values from this sentence

        :param sentence: an object of type Sentence, which will be used to populate the state
        """
        if sentence is not None:
            assert isinstance(sentence, Sentence)
            self.intent_name = sentence.intent.template.name
            self.intent_vector = State._intent_vector_from_sentence(sentence)
            self.sentiment = float(sentence.sentiment)
            self.user_profile = sentence.user_profile
            self.user_profile_vector = State._convert_user_profile(sentence.user_profile)

    def as_vector(self):
        return numpy.concatenate((
            self.intent_vector,
            numpy.array([self.sentiment]),
            self.user_profile_vector
        ))

    @staticmethod
    def _intent_vector_from_sentence(sentence: Sentence) -> ndarray:
        if sentence.intent is None:
            intent_name = 'common.unknown'
        else:
            intent_name = sentence.intent.template.name
        if intent_name not in INTENTS:
            return numpy.zeros(NUM_INTENTS)
        # to_categorical returns a matrix, only take the first column
        return to_categorical(y=INTENTS.index(intent_name), num_classes=NUM_INTENTS)[0]

    @staticmethod
    def _convert_user_profile(user_profile: UserProfile):
        logger.debug('Converting user profile "{}" to vector...'.format(user_profile))
        user_profile = [user_profile.name,
                        user_profile.age,
                        user_profile.has_favourite_player,
                        user_profile.has_favourite_team,
                        user_profile.is_active_player]
        return numpy.array([1 if x is not None else 0 for x in user_profile])

    def __str__(self) -> str:
        return '<State intent={}, sentiment={:.4f}, profile={}>'.format(
            self.intent_name,
            self.sentiment,
            self.user_profile
        )

    def __format__(self, format_spec):
        return self.__str__()