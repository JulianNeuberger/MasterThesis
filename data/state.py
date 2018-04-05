import logging

import numpy
from numpy.core.multiarray import ndarray

from config.models import Configuration
from turns.models import Sentence, UserProfile

logger = logging.getLogger('data')


class State:
    def __init__(self, sentence: Sentence = None):
        """
        creates a new state, if sentence is given, the fields will be populated with values from this sentence

        :param sentence: an object of type Sentence, which will be used to populate the state
        """
        if sentence is not None:
            assert isinstance(sentence, Sentence)
            self.intent_name = sentence.intent.template.name
            self.intent_vector = State._intent_vector_from_sentence(sentence)
            try:
                self._intent_index = Configuration.get_active().state_index_for_name(self.intent_name)
            except ValueError:
                # not in list --> unknown intent
                self._intent_index = Configuration.get_active().state_index_for_name(
                    Configuration.get_active().unknown_intent.name
                )
            self.sentiment = float(sentence.sentiment)
            self.user_profile = sentence.user_profile
            self.user_profile_vector = State._convert_user_profile(sentence.user_profile)

    def as_vector(self):
        return numpy.concatenate((
            self.intent_vector,
            numpy.array([self.sentiment]),
            self.user_profile_vector
        ))

    @property
    def intent_index(self):
        return self._intent_index

    @staticmethod
    def _intent_vector_from_sentence(sentence: Sentence) -> ndarray:
        if sentence.intent is None:
            intent_name = 'common.unknown'
        else:
            intent_name = sentence.intent.template.name
        intent_vector = numpy.zeros(Configuration.get_active().number_state_intents)
        if Configuration.get_active().is_state_intent(intent_name):
            intent_vector[Configuration.get_active().state_index_for_name(intent_name)] = 1.
        return intent_vector

    @staticmethod
    def _convert_user_profile(user_profile: UserProfile):
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
