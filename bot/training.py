import logging
from datetime import datetime

import numpy
from keras.callbacks import TensorBoard
from keras.engine import Model

from bot.config import ACTIONS, BATCH_SIZE, NUM_EPOCHS
from bot.model import get_imagination_model
from data.processing import load_dumped

logger = logging.getLogger('bot')


def train_new_imagination_model():
    model = get_imagination_model()
    model.compile(optimizer='sgd', loss='binary_crossentropy')
    model.summary()

    tensor_board_callback = TensorBoard(log_dir='./logs/{:%d-%m-%Y %H-%M}/'.format(datetime.now()),
                                        batch_size=BATCH_SIZE)
    tensor_board_callback.set_model(model)

    (train_contexts, train_qualities), (test_data) = load_dumped()

    model.fit(train_contexts, train_qualities,
              batch_size=BATCH_SIZE, epochs=NUM_EPOCHS,
              validation_data=test_data,
              callbacks=[tensor_board_callback])

    return model


def predict_on_contexts(model: Model, contexts: numpy.array):
    # states = contexts_to_states(contexts)
    # model.predict(states)
    pass


def prettify_action_qualities(vector):
    vector = zip(ACTIONS, vector)
    vector = sorted(vector, key=lambda x: x[1], reverse=True)
    return ', '.join('{} (Q={:.3})'.format(*entry) for entry in vector)
