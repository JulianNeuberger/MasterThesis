from typing import List

import numpy
from keras.layers import Concatenate, Dense, Input, Layer, Conv1D, Flatten, Dropout, MaxPool1D
from keras.models import Model

from bot.config import STATE_SHAPE, NUM_ACTIONS, IMAGINATION_DEPTH, NUM_INTENTS, SENTIMENT_LEN, \
    USER_PROFILE_LEN, CONTEXT_SHAPE, ACTIONS, IMAGINATION_MODEL_LATEST_WEIGHTS_FILE
from data.context import Context
from events.util import Singleton
from turns.models import Sentence


def get_quality_model(state) -> Layer:
    x = Dense(units=16, use_bias=False, activation='sigmoid')(state)
    x = Dense(units=32, use_bias=False, activation='sigmoid')(x)
    x = Dense(units=16, use_bias=False, activation='sigmoid')(x)

    predicted_quality = Dense(units=NUM_ACTIONS, use_bias=True, activation='linear')(x)
    return predicted_quality


def get_environment_model(state: Layer, quality: Layer, lookahead=IMAGINATION_DEPTH) -> Layer:
    new_state = state
    new_states = []
    predicted_rewards = []

    for t in range(0, lookahead):
        x = Concatenate()([new_state, quality])
        x = Dense(units=32, use_bias=False, activation='relu')(x)

        predicted_reward = Dense(units=1, activation='linear', use_bias=True, name='reward_t{}'.format(t))(x)
        predicted_rewards.append(predicted_reward)

        predicted_intent = Dense(units=NUM_INTENTS, activation='softmax', use_bias=True,
                                 name='intent_t{}'.format(t))(x)
        predicted_sentiment = Dense(units=SENTIMENT_LEN, activation='linear', use_bias=True,
                                    name='sentiment_t{}'.format(t))(x)
        predicted_user_profile = Dense(units=USER_PROFILE_LEN, activation='sigmoid', use_bias=True,
                                       name='profile_t{}'.format(t))(x)

        new_state = Concatenate(name='state_{}_predicted'.format(t + 1))(
            [predicted_intent, predicted_sentiment, predicted_user_profile]
        )
        new_states.append(new_state)

    encoded_imagination = get_encoder(new_states, predicted_rewards)
    aggregated_imagination = get_aggregator(encoded_imagination)

    return aggregated_imagination


def get_aggregator(encodings: List[Layer]) -> Layer:
    return Concatenate()(encodings)


def get_encoder(states: List[Layer], rewards: List[Layer]) -> List[Layer]:
    combined_input = (zip(states, rewards))
    encoding_layer = Dense(units=16)
    encoded_imaginations = []
    for cur in combined_input:
        state, reward = cur
        encoder_input = Concatenate()([state, reward])
        encoded_imaginations.append(encoding_layer(encoder_input))
    return encoded_imaginations


def get_imagination_model() -> Model:
    current_state = Input(shape=STATE_SHAPE)
    quality_model = get_quality_model(current_state)
    imagination = get_environment_model(current_state, quality_model)
    model_free_path = get_quality_model(current_state)

    x = Concatenate()([imagination, model_free_path])

    combined_quality = Dense(units=NUM_ACTIONS, activation='linear', use_bias=True)(x)

    return Model(inputs=[current_state], outputs=[combined_quality])


def get_action_model() -> Model:
    current_state = Input(shape=CONTEXT_SHAPE)

    x = Conv1D(filters=64, kernel_size=(3,), use_bias=False, activation='relu', padding='valid')(current_state)
    x = Dropout(.5)(x)
    x = MaxPool1D(pool_size=2, padding='valid')(x)
    x = Conv1D(filters=128, kernel_size=(1,), use_bias=False, activation='relu', padding='valid')(x)
    x = Dropout(.3)(x)
    x = Conv1D(filters=128, kernel_size=(1,), use_bias=False, activation='relu', padding='valid')(x)
    x = Dropout(.1)(x)
    x = Conv1D(filters=64, kernel_size=(1,), use_bias=False, activation='relu', padding='valid')(x)

    x = Flatten()(x)

    action = Dense(units=NUM_ACTIONS, activation='softmax', use_bias=True)(x)
    return Model(inputs=[current_state], outputs=[action])


class QueryableModel(metaclass=Singleton):
    def __init__(self):
        self._model = get_imagination_model()
        self._model.load_weights(IMAGINATION_MODEL_LATEST_WEIGHTS_FILE)

    def query(self, context: Context, resolve_action_name=False):
        prediction = self._model.predict(context.as_matrix())
        if resolve_action_name:
            return ACTIONS[numpy.argmax(prediction[0])]
        else:
            return prediction[0]

    def query_on_sentence(self, sentence: Sentence):
        state = state_from_sentence(sentence)
        context = state + get
