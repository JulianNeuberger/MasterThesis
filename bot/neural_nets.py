from typing import List

import keras.backend as K
from keras.layers import Concatenate, Dense, Input, Layer, Conv1D, Flatten, Reshape, Lambda, Dropout
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

    combined_quality = Dense(units=NUM_ACTIONS, activation='relu', use_bias=True)(x)

    model = Model(inputs=[state, context], outputs=[combined_quality], name='imagination_model')
    model.compile(optimizer='sgd', loss='mse')
    return model


def get_deep_mind_model(name=None) -> Model:
    state_input = Input(name='state_input', shape=STATE_SHAPE)
    context_input = Input(name='context_input', shape=CONTEXT_SHAPE)

    cxt = Conv1D(filters=32, kernel_size=3)(context_input)
    cxt = Conv1D(filters=32, kernel_size=3)(cxt)
    cxt = Conv1D(filters=32, kernel_size=1)(cxt)
    cxt = Flatten()(cxt)

    x = Concatenate()([state_input, cxt])

    x = Dense(units=128)(x)

    output_layer = Dense(units=NUM_ACTIONS, activation='linear', name='quality_output')(x)

    model = Model(name=name, inputs=[state_input, context_input], outputs=[output_layer])
    model.compile('adam', 'mse')
    return model


def get_simple_model(name=None) -> Model:
    state = Input(name='state_input', shape=STATE_SHAPE)
    action = Input(name='action_input', shape=(NUM_ACTIONS,))

    # x_1 = Flatten()(context)

    x = Concatenate()([state, action])
    # x = Dense(units=128)(x)
    x = Dense(units=2048, use_bias=False, activation='sigmoid')(x)

    x = Dense(units=1)(x)

    model = Model(inputs=[state, action], outputs=[x], name=name)
    model.compile(optimizer='sgd', loss='mse')
    return model


def get_intent_only_model(name=None) -> Model:
    intent = Input(name='intent_input', shape=(1,))
    # x1 = Embedding(NUM_INTENTS, 4, input_length=1)(intent)
    # x1 = keras.backend.squeeze(x1, 1)
    # x1 = Reshape((4,))(x1)

    action = Input(name='action_input', shape=(1,))
    # x2 = Embedding(NUM_ACTIONS, 4, input_length=1)(action)
    # x2 = keras.backend.squeeze(x2, 1)
    # x2 = Reshape((4,))(x2)

    x = Concatenate()([intent, action])

    x = Dropout(.1)(x)
    x = Dense(units=128, use_bias=False)(x)

    x = Dropout(.1)(x)
    x = Dense(units=64, use_bias=False)(x)

    x = Dropout(.25)(x)
    reward = Dense(units=1)(x)

    model = Model(inputs=[intent, action], outputs=[reward], name=name)
    model.compile(optimizer='adam', loss='mse')
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
