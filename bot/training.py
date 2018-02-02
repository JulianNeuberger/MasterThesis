import logging
from datetime import datetime
from typing import List, Tuple, Iterable

import numpy
from keras.callbacks import TensorBoard
from keras.engine import Model

from bot.config import ACTIONS, BATCH_SIZE, NUM_EPOCHS, DISCOUNT
from bot.model import get_imagination_model
from data.context import Context
from data.processing import load_dumped
from data.state import State

logger = logging.getLogger('bot')
graph = None


def train_new_imagination_model():
    model = get_imagination_model()
    model.compile(optimizer='sgd', loss='binary_crossentropy')
    model.summary()

    tensor_board_callback = TensorBoard(log_dir='./logs/{:%d-%m-%Y %H-%M}/'.format(datetime.now()),
                                        batch_size=BATCH_SIZE)
    tensor_board_callback.set_model(model)

    train_contexts, test_contexts = load_dumped()
    train(model, train_contexts, test_contexts, [tensor_board_callback])

    return model


def get_data(contexts: List[Context], model: Model) -> Tuple[numpy.ndarray, numpy.ndarray]:
    xs = numpy.array([context.as_matrix() for context in contexts])
    ys = numpy.array([get_quality_for_context(context, model) for context in contexts])
    return xs, ys


def get_quality_for_context(context: Context, model: Model):
    _, action = context.states[0], context.actions[0]
    if action.terminal:
        return action.reward
    else:
        batch = numpy.array(
            [context.as_matrix()]
        )
        return action.reward + DISCOUNT * model.predict(batch)[0]


def train(model: Model, train_contexts, test_contexts=None, callbacks=None):
    train_xs, train_ys = get_data(train_contexts, model)
    if test_contexts is not None:
        tests_xs, tests_ys = get_data(test_contexts, model)
        model.fit(train_xs, train_ys,
                  batch_size=BATCH_SIZE, epochs=NUM_EPOCHS,
                  validation_data=(tests_xs, tests_ys),
                  callbacks=callbacks)
    model.fit(train_xs, train_ys,
              batch_size=BATCH_SIZE, epochs=NUM_EPOCHS,
              callbacks=callbacks)
    return model


def predict(model: Model, states: Iterable[State], contexts: Iterable[Context]):
    contexts = numpy.array([context.as_matrix() for context in contexts])
    states = numpy.array([state.as_vector() for state in states])
    return model.predict({
        'state_input': states,
        'context_input': contexts
    }, batch_size=BATCH_SIZE)


def prettify_action_qualities(vector):
    vector = zip(ACTIONS, vector)
    vector = sorted(vector, key=lambda x: x[1], reverse=True)
    return ', '.join('{} (Q={:.3})'.format(*entry) for entry in vector)
