import logging
import os
import random
from shutil import copyfile
from typing import Iterable

import numpy
import tensorflow as tf

from bot.callbacks import DiscountCallback, EpsilonCallback
from bot.config import IMAGINATION_MODEL_LATEST_WEIGHTS_FILE, BACKUP_WEIGHTS_FILE, NUM_ACTIONS, BATCH_SIZE, NUM_EPOCHS
from bot.model import get_imagination_model
from data.context import Context
from data.state import State
from events.util import Singleton
from turns.transition import Transition

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
            contexts = numpy.array([context.as_matrix() for context in contexts])
            states = numpy.array([state.as_vector() for state in states])
            return self._model.predict({
                'state_input': states,
                'context_input': contexts
            }, batch_size=BATCH_SIZE)

    def query(self, state: State, context: Context):
        """
        Queries the model with one state and context, returns index of the selected action.
        Selects the action based on the epsilon greedy strategy
        :param state: the current state
        :param context: the context for this state
        :return: an Integer representing the selected action's index
        """
        with self._graph.as_default():
            greedy_prob = (1 - self.current_epsilon()) + (self.current_epsilon() / NUM_ACTIONS)
            greedy = greedy_prob >= random.random()
            if greedy:
                logger.info('Picking action greedily, with probability of {:.4%}'.format(greedy_prob))
                action = self.predict([state], [context])[0]
                return numpy.argmax(action)
            else:
                logger.info('Picking action random, with probability of {:.4%}'.format(1 - greedy_prob))
                return random.randint(0, NUM_ACTIONS - 1)

    def train(self, transitions):
        with self._graph.as_default():
            self._train(transitions, callbacks=[self._discount_callback, self._epsilon_callback])
            QueryableModel._backup_weights()
            QueryableModel._save_weights(self._model)

    @staticmethod
    def _backup_weights():
        logger.info('Backing up weight file...')
        if os.path.isfile(IMAGINATION_MODEL_LATEST_WEIGHTS_FILE):
            copyfile(IMAGINATION_MODEL_LATEST_WEIGHTS_FILE, BACKUP_WEIGHTS_FILE)
            logger.info('Successfully backed up weights.')
        else:
            logger.info('No weight file found!')

    @staticmethod
    def _save_weights(model):
        logger.info('Saving current weights...')
        model.save_weights(IMAGINATION_MODEL_LATEST_WEIGHTS_FILE)
        logger.info('Successfully saved weights.')

    def _train(self, train_data, test_data=None, callbacks=None):
        """
            Trains a given model
            :param train_data: data to train the model with
            :param test_data: (optional) data to evaluate and calculate val_loss against
            :param callbacks: (optional) callbacks, will be passed to keras.fit callbacks
            :return: the original model with updated weights
            """
        states, contexts, qualities = Transition.transitions_to_data(train_data, self)
        if test_data is not None:
            logger.info("Training with validation data: {}".format(test_data))
            test_states, test_contexts, test_qualities = Transition.transitions_to_data(test_data, self)
            self._model.fit({'state_input': states, 'context_input': contexts}, qualities,
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
            self._model.fit({'state_input': states, 'context_input': contexts}, qualities,
                            batch_size=BATCH_SIZE, epochs=NUM_EPOCHS,
                            callbacks=callbacks)
        return self._model
