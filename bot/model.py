from keras import Input
from keras.layers import Concatenate, Dense

from bot.config import STATE_SHAPE, ACTIONS, NUM_ACTIONS, IMAGINATION_DEPTH


def get_future_model(action, state):
    """
    Models user behaviour, so we can predict how states change depending on our actions
    """
    x = Concatenate()([action, state])
    state = Dense(units=STATE_SHAPE)(x)
    reward = Dense(units=1)(x)
    return state, reward


def get_policy_model(state):
    x = Dense(units=NUM_ACTIONS)(state)
    return x


def get_imagination_core(state):
    action = get_policy_model(state)
    future_state, reward = get_future_model(action, state)
    return future_state, reward


def get_roll_out_encoder(state, reward):
    x = Concatenate()([state, reward])
    x = Dense(units=16)(x)
    return x


def get_single_imagination_roll_out(state, depth=IMAGINATION_DEPTH):
    encoded_imagination = []
    for _ in range(0, depth):
        state, reward = get_imagination_core(state)
        encoded_imagination.append(get_roll_out_encoder(state, reward))
    return Concatenate()(encoded_imagination)


def get_imagination_aggregator(roll_outs):
    x = Concatenate()(roll_outs)
    return x


def get_total_model():
    state = Input(shape=STATE_SHAPE)

    roll_outs = [get_single_imagination_roll_out(state) for _ in ACTIONS]
    aggregated_roll_outs = get_imagination_aggregator(roll_outs)
    model_free = get_policy_model(state)
    x = Concatenate()([aggregated_roll_outs, model_free])
    policy = Dense(units=NUM_ACTIONS, activation='softmax')(x)
    return policy
