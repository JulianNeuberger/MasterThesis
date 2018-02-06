import logging
from datetime import datetime
from typing import List, Iterable

import numpy
from keras.callbacks import TensorBoard
from keras.engine import Model

from bot.config import ACTIONS, BATCH_SIZE, NUM_EPOCHS
from bot.model import get_imagination_model
from data.context import Context
from data.processing import load_dumped
from data.state import State
from turns.transition import Transition

logger = logging.getLogger('bot')
graph = None


def train_new_imagination_model():
    model = get_imagination_model()
    tensor_board_callback = TensorBoard(log_dir='./logs/{:%d-%m-%Y %H-%M}/'.format(datetime.now()),
                                        batch_size=BATCH_SIZE)
    tensor_board_callback.set_model(model)

    train_data, test_data = load_dumped()
    train(model, train_data, test_data, [tensor_board_callback])

    return model


def train(model: Model, train_data: List[Transition], test_data: List[Transition] = None, callbacks=None):
    """
    Trains a given model
    :param model: the model to train
    :param train_data: data to train the model with
    :param test_data: data to evaluate and calculate val_loss against
    :param callbacks: callbacks, will be passed to keras.fit callbacks
    :return: the original model with updated weights
    """
    states, contexts, qualities = transitions_to_data(train_data, model)
    if test_data is not None:
        logger.info("Training with validation data: {}".format(test_data))
        test_states, test_contexts, test_qualities = transitions_to_data(test_data, model)
        model.fit({'state_input': states, 'context_input': contexts}, qualities,
                  batch_size=BATCH_SIZE, epochs=NUM_EPOCHS,
                  validation_data=(
                      {
                          'state_input': test_states,
                          'context_input': test_contexts
                      },
                      test_qualities
                  ),
                  callbacks=callbacks)
    else:
        logger.warning("Training without validation data. This will tamper with logs for tensor board!")
        model.fit({'state_input': states, 'context_input': contexts}, qualities,
                  batch_size=BATCH_SIZE, epochs=NUM_EPOCHS,
                  callbacks=callbacks)
    return model


def predict(model, states: Iterable[State], contexts: Iterable[Context]):
    contexts = numpy.array([context.as_matrix() for context in contexts])
    states = numpy.array([state.as_vector() for state in states])
    return model.predict({
        'state_input': states,
        'context_input': contexts
    }, batch_size=BATCH_SIZE)


def transitions_to_data(transitions: List[Transition], model: Model):
    states = []
    contexts = []
    qualities = []
    for transition in transitions:
        state, context, quality = transition.to_data_tuple(model)
        states.append(state)
        contexts.append(context)
        qualities.append(quality)
    return numpy.array(states), numpy.array(contexts), numpy.array(qualities)


def prettify_action_qualities(vector):
    vector = zip(ACTIONS, vector)
    vector = sorted(vector, key=lambda x: x[1], reverse=True)
    return ', '.join('{} (Q={:.3})'.format(*entry) for entry in vector)
