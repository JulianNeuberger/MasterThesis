from keras import Input
from keras.layers import Concatenate, Dense
from keras.models import Model

from bot.config import STATE_SHAPE, ACTIONS, NUM_ACTIONS, IMAGINATION_DEPTH


def get_future_model(action, state, model_id):
    """
    Models user behaviour, so we can predict how states change depending on our actions
    """
    x = Concatenate(name='future_model_{}_input'.format(model_id))([action, state])
    state = Dense(units=STATE_SHAPE[0], name='predicted_state_{}'.format(model_id))(x)
    reward = Dense(units=1, name='predicted_reward_{}'.format(model_id))(x)
    return state, reward


def get_policy_model(state, path_id):
    x = Dense(units=NUM_ACTIONS, name='quality_{}_output'.format(path_id))(state)
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
