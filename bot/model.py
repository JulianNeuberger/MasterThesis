from typing import List

import keras.backend as K
from keras.layers import Concatenate, Dense, Input, Layer, Conv1D, Flatten, Reshape, Lambda
from keras.models import Model

from bot.config import NUM_ACTIONS, IMAGINATION_DEPTH, NUM_INTENTS, SENTIMENT_LEN, \
    USER_PROFILE_LEN, CONTEXT_SHAPE, STATE_SHAPE


def get_quality_model(state, contexts) -> Layer:
    x = Conv1D(filters=16, kernel_size=3, use_bias=False, activation='sigmoid', padding='same')(contexts)
    x = Conv1D(filters=32, kernel_size=3, use_bias=False, activation='sigmoid', padding='same')(x)
    x = Conv1D(filters=16, kernel_size=3, use_bias=False, activation='sigmoid', padding='same')(x)
    x = Conv1D(filters=16, kernel_size=1, use_bias=False, activation='sigmoid', padding='same')(x)
    x = Conv1D(filters=16, kernel_size=1, use_bias=False, activation='sigmoid', padding='same')(x)

    x = Flatten()(x)

    x = Concatenate()([state, x])
    x = Dense(units=64)(x)

    predicted_quality = Dense(units=NUM_ACTIONS, use_bias=True, activation='linear')(x)
    return predicted_quality


def get_environment_model(state: Layer, context: Layer, lookahead=IMAGINATION_DEPTH) -> Layer:
    # output for the aggregator
    new_states = []
    predicted_rewards = []

    for t in range(0, lookahead):
        predicted_action = get_quality_model(state, context)

        x = Flatten()(context)
        x = Concatenate()([state, x, predicted_action])

        predicted_reward = \
            Dense(units=32, use_bias=False, activation='relu', name='reward_t{}_predicted'.format(
                t
            ))(x)

        predicted_rewards.append(predicted_reward)

        predicted_intent = Dense(units=NUM_INTENTS, activation='softmax', use_bias=True,
                                 name='intent_t{}'.format(t))(x)
        predicted_sentiment = Dense(units=SENTIMENT_LEN, activation='linear', use_bias=True,
                                    name='sentiment_t{}'.format(t))(x)
        predicted_user_profile = Dense(units=USER_PROFILE_LEN, activation='sigmoid', use_bias=True,
                                       name='profile_t{}'.format(t))(x)

        predicted_state = Concatenate(name='state_t{}_predicted'.format(t + 1))(
            [predicted_intent, predicted_sentiment, predicted_user_profile]
        )
        predicted_context = Concatenate(name='context_t{}_predicted'.format(t + 1))(
            [predicted_state, predicted_action]
        )
        predicted_context = Reshape(target_shape=(1, STATE_SHAPE[0] + NUM_ACTIONS,))(predicted_context)

        context = Reshape(target_shape=CONTEXT_SHAPE)(context)
        context = Lambda(push_context, output_shape=push_context_out_shape, name='context_t{}'.format(t + 1))(
            [context, predicted_context])

        state = predicted_state

        new_states.append(predicted_state)

    encoded_imagination = get_encoder(new_states, predicted_rewards)
    aggregated_imagination = get_aggregator(encoded_imagination)

    return aggregated_imagination


def get_aggregator(encodings: List[Layer]) -> Layer:
    return Concatenate()(encodings)


def get_encoder(states: List[Layer], rewards: List[Layer]) -> List[Layer]:
    combined_input = (zip(states, rewards))
    encoding_layer = Dense(units=16, name="state/reward-encoder")
    encoded_imaginations = []
    step = 0
    for cur in combined_input:
        state, reward = cur
        encoder_input = Concatenate(name="encoding_input_t{}".format(step))([state, reward])
        encoded_imaginations.append(encoding_layer(encoder_input))
        step += 1
    return encoded_imaginations


def get_imagination_model() -> Model:
    context = Input(name='context_input', shape=CONTEXT_SHAPE)
    state = Input(name='state_input', shape=STATE_SHAPE)

    imagination = get_environment_model(state, context)
    model_free_path = get_quality_model(state, context)

    x = Concatenate()([imagination, model_free_path])

    combined_quality = Dense(units=NUM_ACTIONS, activation='linear', use_bias=True)(x)

    model = Model(inputs=[state, context], outputs=[combined_quality])
    model.compile(optimizer='sgd', loss='binary_crossentropy')

    return model


def push_context(x):
    assert len(x) == 2
    contexts, context = x[0], x[1]
    ret = [context]
    for i in range(1, contexts.shape[1]):
        ret.append(contexts[:, i:i + 1])
    ret = K.stack(ret)
    shape = K.shape(contexts)
    ret = K.reshape(ret, shape)
    return ret


def push_context_out_shape(in_shape):
    assert len(in_shape) == 2
    contexts_shape = in_shape[0]
    return contexts_shape
