import logging
from datetime import datetime
from typing import List

import numpy
from keras.callbacks import TensorBoard
from keras.engine import Model

from bot.config import ACTIONS, BATCH_SIZE, NUM_EPOCHS, DISCOUNT, STATE_SHAPE
from bot.model import get_imagination_model
from data.processing import load_dumped
from data.transition import Transition

logger = logging.getLogger('bot')


def train_new_imagination_model():
    model = get_imagination_model()
    model.compile(optimizer='sgd', loss='binary_crossentropy')
    model.summary()

    train_contexts, test_contexts = load_dumped()

    return train_on_contexts(model, train_contexts, test_contexts)


def predict_on_contexts(model: Model, contexts: numpy.array):
    states = contexts_to_states(contexts)
    model.predict(states)


def train_on_contexts(model: Model, train_contexts, test_contexts):
    tensor_board_callback = TensorBoard(log_dir='./logs/{:%d-%m-%Y %H-%M}/'.format(datetime.now()),
                                        batch_size=BATCH_SIZE)
    tensor_board_callback.set_model(model)

    model.fit(contexts_to_states(train_contexts),
              contexts_to_qualities(train_contexts, model, DISCOUNT),
              batch_size=BATCH_SIZE, epochs=NUM_EPOCHS,
              validation_data=(
                  contexts_to_states(test_contexts),
                  contexts_to_qualities(test_contexts, model, DISCOUNT)
              ),
              callbacks=[tensor_board_callback])

    return model


def prettify_action_qualities(vector):
    vector = zip(ACTIONS, vector)
    vector = sorted(vector, key=lambda x: x[1], reverse=True)
    return ', '.join('{} (Q={:.3})'.format(*entry) for entry in vector)


def context_to_state(context: List[Transition]):
    state_context = []
    for transition in context:
        if transition is not None:
            state_context.append(transition.state)
        else:
            state_context.append(numpy.zeros(STATE_SHAPE))
    return state_context


def contexts_to_states(contexts: List[List[Transition]]):
    state_contexts = []
    for context in contexts:
        state_contexts.append(context_to_state(context))
    return numpy.array(state_contexts)


def context_to_quality(context: List[Transition], model: Model, discount: float = DISCOUNT):
    last_transition = context[-1]
    quality = predict_on_contexts(model, numpy.array([context]))[0]
    action_index = numpy.argmax(last_transition.action)
    if last_transition.terminal is True:
        # this is the last action in the sequence, do not use discounting
        quality[action_index] = last_transition.reward
    else:
        next_state = last_transition.next_state
        next_state = numpy.array([next_state])
        future_value = model.predict(next_state)[0]
        # in the middle of a sequence, use discounting
        quality[action_index] = last_transition.reward + discount * numpy.max(future_value)
    return quality


def contexts_to_qualities(contexts, model, discount: float = DISCOUNT):
    qualities = []
    for context in contexts:
        qualities.append(context_to_quality(context, model, discount))
    return numpy.array(qualities)
