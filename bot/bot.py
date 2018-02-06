import logging
import os
import random
from shutil import copyfile
from typing import Iterable

import numpy
import tensorflow as tf

from bot.callbacks import DiscountCallback, EpsilonCallback
from bot.config import IMAGINATION_MODEL_LATEST_WEIGHTS_FILE, BACKUP_WEIGHTS_FILE, NUM_ACTIONS
from bot.model import get_imagination_model
from bot.training import predict, train
from data.context import Context
from data.state import State
from events.util import Singleton

logger = logging.getLogger("bot")


class QueryableModel(metaclass=Singleton):
    """
    A Singleton, that holds a keras model and can be trained, be queried and predict actions.
    The core of the chat bot
    """

    def __init__(self, load=True):
        """
        Gets/Creates a QueryableModel (singleton!). Initializes the keras.model and Discount/EpsilonCallbacks

        :param load: bool, should weights be loaded form the default file? Defaults to True
        """
        self._model = get_imagination_model()
        self._graph = tf.get_default_graph()
        self._discount_callback = DiscountCallback()
        self._epsilon_callback = EpsilonCallback()
        if load and os.path.isfile(IMAGINATION_MODEL_LATEST_WEIGHTS_FILE):
            logger.info('Loading model weights from "{}".'.format(IMAGINATION_MODEL_LATEST_WEIGHTS_FILE))
            self._model.load_weights(IMAGINATION_MODEL_LATEST_WEIGHTS_FILE)

    def current_discount(self):
        return self._discount_callback.value

    def current_epsilon(self):
        return self._epsilon_callback.value

    def predict(self, states: Iterable[State], contexts: Iterable[Context]):
        """
        Simple delegate for the keras.model.predict function
        :param states: current States
        :param contexts: the Contexts corresponding to given States
        :return: an array of quality vectors for each input row (state/context pair)
        """
        with self._graph.as_default():
            return predict(self._model, states, contexts)

    def query(self, state: State, context: Context):
        """
        Queries the model with one state and context, returns index of the selected action.
        Selects the action based on the epsilon greedy strategy
        :param state: the current state
        :param context: the context for this state
        :return: an Integer representing the selected action's index
        """
        with self._graph.as_default():
            greedy = (1 - self.current_epsilon()) + (self.current_epsilon() / NUM_ACTIONS) >= random.random()
            if greedy:
                action = predict(self._model, numpy.array([state]), numpy.array([context]))[0]
                return numpy.argmax(action)
            else:
                return random.randint(0, NUM_ACTIONS - 1)

    def train(self, transitions):
        with self._graph.as_default():
            train(self._model, transitions, callbacks=[self._discount_callback, self._epsilon_callback])
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
