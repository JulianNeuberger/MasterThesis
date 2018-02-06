import logging
import os
from shutil import copyfile
from typing import Iterable

import tensorflow as tf

from bot.callbacks import DiscountCallback
from bot.config import IMAGINATION_MODEL_LATEST_WEIGHTS_FILE, BACKUP_WEIGHTS_FILE
from bot.model import get_imagination_model
from bot.training import predict, train
from data.context import Context
from data.state import State
from events.util import Singleton

logger = logging.getLogger("bot")


class QueryableModel(metaclass=Singleton):
    def __init__(self, load=True):
        self._model = get_imagination_model()
        self._graph = tf.get_default_graph()
        self._episodes_seen = 0
        self._discount_callback = DiscountCallback()
        if load and os.path.isfile(IMAGINATION_MODEL_LATEST_WEIGHTS_FILE):
            logger.info('Loading model weights from "{}".'.format(IMAGINATION_MODEL_LATEST_WEIGHTS_FILE))
            self._model.load_weights(IMAGINATION_MODEL_LATEST_WEIGHTS_FILE)

    def current_discount(self):
        return self._discount_callback.discount

    def query(self, states: Iterable[State], contexts: Iterable[Context]):
        with self._graph.as_default():
            return predict(self._model, states, contexts)

    def train(self, transitions):
        with self._graph.as_default():
            train(self._model, transitions, callbacks=[self._discount_callback])
            QueryableModel._backup_weights()
            QueryableModel._save_weights(self._model)

    @staticmethod
    def _backup_weights():
        logger.info('Backing up weight file...')
        copyfile(IMAGINATION_MODEL_LATEST_WEIGHTS_FILE, BACKUP_WEIGHTS_FILE)
        logger.info('Successfully backed up weights.')

    @staticmethod
    def _save_weights(model):
        logger.info('Saving current weights...')
        model.save_weights(IMAGINATION_MODEL_LATEST_WEIGHTS_FILE)
        logger.info('Successfully saved weights.')
