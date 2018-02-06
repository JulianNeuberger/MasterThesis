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


def prettify_action_qualities(vector):
    vector = zip(ACTIONS, vector)
    vector = sorted(vector, key=lambda x: x[1], reverse=True)
    return ', '.join('{} (Q={:.3})'.format(*entry) for entry in vector)
