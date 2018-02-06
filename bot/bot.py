import os
from typing import Iterable

import tensorflow as tf

from bot.callbacks import DiscountCallback
from bot.config import IMAGINATION_MODEL_LATEST_WEIGHTS_FILE, WEIGHTS_DIR
from bot.model import get_imagination_model
from bot.training import predict, train
from data.context import Context
from data.state import State
from events.util import Singleton


class QueryableModel(metaclass=Singleton):
    def __init__(self):
        self._model = get_imagination_model()
        self._graph = tf.get_default_graph()
        self._episodes_seen = 0
        self._discount_callback = DiscountCallback()
        if os.path.isfile(IMAGINATION_MODEL_LATEST_WEIGHTS_FILE):
            self._model.load_weights(IMAGINATION_MODEL_LATEST_WEIGHTS_FILE)

    def current_discount(self):
        return self._discount_callback.discount

    def query(self, states: Iterable[State], contexts: Iterable[Context]):
        with self._graph.as_default():
            return predict(self._model, states, contexts)

    def train(self, transitions):
        with self._graph.as_default():
            train(self._model, transitions, callbacks=[self._discount_callback])
            self._model.save_weights(WEIGHTS_DIR)
