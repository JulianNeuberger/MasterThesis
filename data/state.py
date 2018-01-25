from keras.utils import to_categorical

from bot.config import INTENTS, NUM_INTENTS
from data.exceptions import NoStateIntentError
from turns.models import Sentence, UserProfile


class State:
    intent_vector = None
    sentiment = 0
    user_profile_vector = None

    def __init__(self, sentence: Sentence = None):
        """
        creates a new state, if sentence is given, the fields will be populated with values from this sentence

        :param sentence: an object of type Sentence, which will be used to populate the state

        :raises NoStateIntentError: when the intent of an sentence is not in the set of state-intents,
                aka. intents that can be said by the user
        """
        if sentence is not None:
            assert isinstance(sentence, Sentence)
            self.intent_vector = State._intent_vector_from_sentence(sentence)
            self.sentiment = sentence.sentiment
            self.user_profile_vector = State._convert_user_profile(sentence.user_profile)

    @staticmethod
    def _intent_vector_from_sentence(sentence: Sentence):
        if sentence.intent is None:
            intent_name = 'common.unknown'
        else:
            intent_name = sentence.intent.template.name
        if intent_name not in INTENTS:
            raise NoStateIntentError(sentence.intent)
        return to_categorical(y=INTENTS.index(intent_name), num_classes=NUM_INTENTS)

    @staticmethod
    def _convert_user_profile(user_profile: UserProfile):
        user_profile = [user_profile.name,
                        user_profile.age,
                        user_profile.has_favourite_player,
                        user_profile.has_favourite_team,
                        user_profile.is_active_player]
        return [1 if x is not None else 0 for x in user_profile]
