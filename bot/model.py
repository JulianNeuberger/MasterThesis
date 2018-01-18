from typing import List

from keras.layers import Concatenate, Dense, Input, Layer, Conv1D, Flatten, Dropout, MaxPool1D
from keras.models import Model

from bot.config import STATE_SHAPE, ACTIONS, NUM_ACTIONS, IMAGINATION_DEPTH, NUM_INTENTS, SENTIMENT_LEN, \
    USER_PROFILE_LEN, CONTEXT_SHAPE


def get_future_model(action, state, model_id):
    """
    Models user behaviour, so we can predict how states change depending on our actions
    """
    x = Concatenate(name='future_model_{}_input'.format(model_id))([action, state])
    x = Dense(units=32, use_bias=False, activation='sigmoid',
              name='future_model_{}_hidden'.format(model_id))(x)
    # x = Conv1D(filters=16, kernel_size=(3,), use_bias=False, padding='same')(x)
    # x = Conv1D(filters=16, kernel_size=(3,), use_bias=False, padding='same')(x)
    # x = Flatten()(x)
    state = Dense(units=STATE_SHAPE[0], name='predicted_state_{}'.format(model_id))(x)
    reward = Dense(units=1, name='predicted_reward_{}'.format(model_id))(x)
    return state, reward


def get_policy_model(state, path_id):
    x = Dense(units=16, use_bias=False, activation='relu',
              name='quality_{}_input'.format(path_id))(state)

    x = Dense(units=32, use_bias=False, activation='relu',
              name='quality_{}_hidden_1'.format(path_id))(x)

    x = Dense(units=16, use_bias=False, activation='relu',
              name='quality_{}_hidden_2'.format(path_id))(x)

    x = Dense(units=NUM_ACTIONS, use_bias=True, activation='softmax',
              name='quality_{}_output'.format(path_id))(x)
    return x


def get_imagination_core(state, current_core_id):
    action = get_policy_model(state, current_core_id)
    future_state, reward = get_future_model(action, state, current_core_id)
    return future_state, reward


def get_roll_out_encoder(state, reward, encoder_id):
    x = Concatenate(name='roll_out_encoder_{}_input'.format(encoder_id))([state, reward])
    x = Dense(units=16, name='roll_out_encoding_{}'.format(encoder_id))(x)
    return x


def get_single_imagination_roll_out(state, action_id, depth=IMAGINATION_DEPTH):
    encoded_imagination = []
    for cur_depth in range(0, depth):
        core_id = '{}_{}'.format(action_id, cur_depth)
        state, reward = get_imagination_core(state, core_id)
        encoded_imagination.append(get_roll_out_encoder(state, reward, core_id))
    return Concatenate()(encoded_imagination)


def get_imagination_aggregator(roll_outs):
    x = Concatenate(name='imagination_aggregator')(roll_outs)
    return x


def get_total_model() -> Model:
    state = Input(shape=STATE_SHAPE)

    roll_outs = [get_single_imagination_roll_out(state, action) for action in ACTIONS]
    aggregated_roll_outs = get_imagination_aggregator(roll_outs)
    model_free = get_policy_model(state, 'model_free_path')
    x = Concatenate()([aggregated_roll_outs, model_free])
    policy = Dense(units=NUM_ACTIONS, activation='softmax', name='quality_output')(x)

    return Model(state, policy)


def get_quality_model(state) -> Layer:
    x = Dense(units=16, use_bias=False, activation='sigmoid')(state)
    x = Dense(units=32, use_bias=False, activation='sigmoid')(x)
    x = Dense(units=16, use_bias=False, activation='sigmoid')(x)

    predicted_quality = Dense(units=NUM_ACTIONS, use_bias=True, activation='linear')(x)
    return predicted_quality


def get_environment_model(state, quality, lookahead=IMAGINATION_DEPTH) -> Layer:
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

        new_state = Concatenate()([predicted_intent, predicted_sentiment, predicted_user_profile])
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
