import logging
import os
import random
from shutil import copyfile
from typing import Iterable

import numpy
import tensorflow as tf
from keras.callbacks import TensorBoard

from bot.callbacks import DiscountCallback, EpsilonCallback, TargetResetCallback
from bot.config import IMAGINATION_MODEL_LATEST_WEIGHTS_FILE, BACKUP_WEIGHTS_FILE, NUM_ACTIONS, BATCH_SIZE, \
    NUM_EPOCHS, ACTIONS, TEST_RATIO, LOG_DIR
from bot.model import get_simple_model
from data.action import Action
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
        # self._model = get_imagination_model()
        self._model = get_simple_model()
        self._target = get_simple_model()
        self._graph = tf.get_default_graph()
        self._discount_callback = DiscountCallback()
        self._epsilon_callback = EpsilonCallback()
        self._reset_callback = TargetResetCallback(self._model, self._target)
        self._tensor_board_callback = TensorBoard(log_dir=os.path.join(LOG_DIR, self._model.name))
        self._epochs_trained = 0
        if load and os.path.isfile(IMAGINATION_MODEL_LATEST_WEIGHTS_FILE):
            logger.info('Loading model weights from "{}".'.format(IMAGINATION_MODEL_LATEST_WEIGHTS_FILE))
            self._model.load_weights(IMAGINATION_MODEL_LATEST_WEIGHTS_FILE)

    def current_discount(self):
        return self._discount_callback.value

    def current_epsilon(self):
        return self._epsilon_callback.value

    def predict(self, states: Iterable[State], action_indices: Iterable[int], contexts: Iterable[Context]):
        """
        Simple delegate for the keras.model.predict function
        :param action_indices: action indices to use
        :param states: current States
        :param contexts: the Contexts corresponding to given States
        :return: an array of quality vectors for each input row (state/context pair)
        """
        with self._graph.as_default():
            contexts = numpy.array([context.as_matrix() for context in contexts])
            states = numpy.array([state.as_vector() for state in states])
            action_indices = numpy.array([Action.vector_from_name(ACTIONS[index]) for index in action_indices])
            return self._model.predict({
                'state_input': states,
                'action_input': action_indices,
                'context_input': contexts
            }, batch_size=BATCH_SIZE)

    def query(self, state: State, context: Context) -> str:
        """
        Queries the model with one state and context, returns index of the selected action.
        Selects the action based on the epsilon greedy strategy
        :param state: the current state
        :param context: the context for this state
        :return: name of action to use
        """
        with self._graph.as_default():
            greedy_prob = (1 - self.current_epsilon()) + (self.current_epsilon() / NUM_ACTIONS)
            greedy = greedy_prob >= numpy.random.random()
            if greedy:
                logger.info('Picking action greedily, with probability of {:.4%}'.format(greedy_prob))
                action = self._optimal_action(state, context)
                return action
            else:
                logger.info('Picking action random, with probability of {:.4%}'.format(1 - greedy_prob))
                return ACTIONS[random.randint(0, NUM_ACTIONS - 1)]

    def _optimal_action(self, state: State, context: Context) -> str:
        optimal_action = None
        optimal_value = float('-inf')
        for index, _ in enumerate(ACTIONS):
            value = self.predict([state], [index], [context])
            if value > optimal_value:
                optimal_action = ACTIONS[index]
                optimal_value = value
        logger.info('Optimal action for state {} is {} with value of {}'.format(state, optimal_action, optimal_value))
        return optimal_action

    def train(self, transitions):
        with self._graph.as_default():
            # epochs is not number of iterations, but the target epoch "id", see keras.fit documentation
            target_epoch = self._epochs_trained + NUM_EPOCHS
            states, contexts, actions, qualities = Transition.transitions_to_data(transitions, self)
            self._model.fit({
                'state_input': states,
                'context_input': contexts,
                'action_input': actions},
                qualities,
                batch_size=BATCH_SIZE, epochs=target_epoch, initial_epoch=self._epochs_trained,
                validation_split=TEST_RATIO,
                callbacks=[
                    self._discount_callback,
                    self._epsilon_callback,
                    self._reset_callback,
                    self._tensor_board_callback
                ])
            QueryableModel._backup_weights()
            QueryableModel._save_weights(self._model)
            self._epochs_trained += NUM_EPOCHS

    def action_to_quality(self, action, state_t0, context, state_t1) -> float:
        if action.terminal:
            return action.reward
        else:
            context = context.push(state_t0, action)
            q_t2 = self.predict([state_t1], [action.index], [context])[0]
            return action.reward + self.current_discount() * q_t2

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
