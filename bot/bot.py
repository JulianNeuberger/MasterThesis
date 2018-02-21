import logging
import os
from shutil import copyfile
from typing import Dict, Optional, Tuple

import numpy
import tensorflow as tf
from keras.callbacks import TensorBoard

from bot.callbacks import DiscountCallback, EpsilonCallback, TargetResetCallback
from bot.config import BATCH_SIZE, ACTIONS, TEST_RATIO, LOG_DIR, WEIGHTS_DIR, CONTEXT_LENGTH, NUM_ACTIONS, STATE_SHAPE, \
    CONTEXT_SHAPE
from bot.model import get_deep_mind_model
from data.action import Action
from data.context import Context
from data.state import State
from data.turn import Turn
from events.util import Singleton
from turns.models import Sentence
from turns.transition import Transition

logger = logging.getLogger("bot")


class QueryableModelInterface(metaclass=Singleton):
    """
    A Singleton, that holds a keras model and can be trained, be queried and predict actions.
    The core of the chat bot.
    Extend this class to use your models and logic. Implement at least methods _init_model
    """

    instance = None

    def __init__(self, model_name: str, load=True):
        """
        Gets/Creates a QueryableModel (singleton!). Initializes the keras.model and Discount/EpsilonCallbacks

        :param load: bool, should weights be loaded form the default file? Defaults to True
        """
        self._callbacks = []
        self._model = None
        self._epochs_trained = 0
        self._graph = tf.get_default_graph()

        self._model_base_name = model_name

        self._init_model(load)
        assert self._model is not None, 'Method _init_model has to set _model member!'
        self._init_callbacks()
        if QueryableModelInterface.instance is None:
            QueryableModelInterface.instance = self

    def _init_model(self, *args, **kwargs):
        """
        Initializes the underlying keras model used by this QueryableModel.
        Implementation should set the self._model member and is mandatory.
        """
        raise NotImplementedError

    def _init_callbacks(self):
        """
        Initializes callbacks needed for this model.
        Implement to specify callbacks used.
        Defaults to using only TensorBoard callback.
        """
        self._callbacks = [TensorBoard(log_dir=os.path.join(LOG_DIR, self._model.name))]

    def predict(self, inputs: Dict[str, numpy.ndarray]):
        """
        Simple delegate for the keras.model.predict function

        :param inputs: input as dict of input_name->numpy.ndarray
        :return: an array of quality vectors for each input row (state/context pair), not processed,
                    see keras.model.predict
        """
        with self._graph.as_default():
            return self._model.predict(inputs, batch_size=BATCH_SIZE)

    def query(self, raw_input) -> str:
        """
        Queries the model directly on some raw input. This input has to be exactly one sample!
        Defaults to simply greedily querying the model with given data,
        converting the prediction to an action and returning its name.
        Override this method for custom behaviour (like epsilon greedy strategies)

        :param raw_input: Some raw input the model depends on

        :return: names of the chosen action, will always be a list, even only with one element!
        """
        with self._graph.as_default():
            return self._prediction_to_action(self._model.predict(raw_input))

    def train(self):
        with self._graph.as_default():
            batch = self._sample_batches()
            if batch is not None:
                inputs, outputs = batch
                # epochs is not number of iterations, but the target epoch "id", see keras.fit documentation
                target_epoch = self._epochs_trained + 1
                self._model.fit(inputs, outputs,
                                batch_size=BATCH_SIZE,
                                epochs=target_epoch, initial_epoch=self._epochs_trained,
                                validation_split=TEST_RATIO,
                                callbacks=self._callbacks)
                self._epochs_trained += 1

    def save_weights(self):
        with self._graph.as_default():
            self._backup_weights()
            self._save_weights()

    def _sample_batches(self) -> Optional[Tuple[Dict, Dict]]:
        """
        Method for sampling batches (0-*) to use in training.
        Can return None, if training not possible.
        Method is responsible for ordering/shuffling samples.

        Implement this method!

        :return: None, if no training possible, a tuple of dicts of inputs and outputs otherwise
        """
        raise NotImplementedError()

    def _prediction_to_action(self, prediction: numpy.ndarray) -> str:
        """
        Implement this to process a raw model prediction into an action name

        :param prediction: a 1D numpy array resulting from querying the model (2nd dimension squeezed)

        :returns: a action name string
        """
        raise NotImplementedError()

    def _backup_weights(self):
        logger.info('Backing up weight file...')
        if not os.path.exists(WEIGHTS_DIR):
            os.makedirs(WEIGHTS_DIR)
        weight_file, backup_file, weight_dir = self._get_model_weights_file_names()
        if not os.path.exists(weight_dir):
            os.makedirs(weight_dir)
        if os.path.isfile(weight_file):
            copyfile(weight_file, backup_file)
            logger.info('Successfully backed up weights.')

    def _save_weights(self):
        weight_file_name, _, _ = self._get_model_weights_file_names()
        logger.info('Saving current weights...')
        self._model.save_weights(weight_file_name)
        logger.info('Successfully saved weights.')

    def _get_model_weights_file_names(self):
        model_weight_dir = os.path.join(WEIGHTS_DIR, self._model.name)
        model_weight_file = os.path.join(model_weight_dir, 'weights.pickle')
        backup_file = os.path.join(model_weight_dir, 'weights.pickle.bkp')
        return model_weight_file, backup_file, model_weight_dir


class DeepMindModel(QueryableModelInterface):
    def __init__(self, bot_user):
        super().__init__('deep_mind_model')
        self._bot_user = bot_user

    def _init_model(self, load=True):
        num_models = len([name for name in os.listdir(LOG_DIR) if
                          os.path.isdir(os.path.join(LOG_DIR, name)) and self._model_base_name in name])
        model_number = num_models if not load else num_models - 1
        model_name = '{}_v{:03d}'.format(self._model_base_name, model_number)
        self._model = get_deep_mind_model(name=model_name)
        self._target = get_deep_mind_model()
        if load:
            model_weights_file, _, _ = self._get_model_weights_file_names()
            if os.path.isfile(model_weights_file):
                logger.info('Loading model weights from "{}".'.format(model_weights_file))
                self._model.load_weights(model_weights_file)
                self._target.load_weights(model_weights_file)
            else:
                logger.info(
                    'No weights file for model "{}" found, this can be due to the first time running this model...'.
                        format(self._model.name))

    def _init_callbacks(self):
        self._discount_callback = DiscountCallback()
        self._epsilon_callback = EpsilonCallback()
        super()._init_callbacks()
        self._callbacks.extend([
            self._epsilon_callback,
            self._discount_callback,
            TargetResetCallback(self._model, self._target)
        ])

    @property
    def discount(self):
        return self._discount_callback.value

    @property
    def epsilon(self):
        return self._epsilon_callback.value

    def _sample_batches(self) -> Optional[Tuple[Dict, Dict]]:
        if Sentence.objects.count() == 0:
            return None
        sentences = \
            [Sentence.sample_bot_sentence_uniform_random(self._bot_user.username) for _ in range(0, BATCH_SIZE)]
        transitions = []
        for sentence in sentences:
            context_sentences = Sentence.objects \
                                    .filter(said_in=sentence.said_in, said_on__lte=sentence.said_on) \
                                    .order_by('-said_on')[:CONTEXT_LENGTH * 2 + 4]
            context_sentences = list(context_sentences)
            assert len(context_sentences) >= 4
            a1 = Action(context_sentences.pop(0))
            s1 = State(context_sentences.pop(0))
            turns = Turn.sentences_to_turns(context_sentences[:-2], self._bot_user)
            context_t1 = Context.get_single_context(turns, CONTEXT_LENGTH)
            a0 = Action(context_sentences.pop(0))
            s0 = State(context_sentences.pop(0))
            turns = Turn.sentences_to_turns(context_sentences, self._bot_user)
            context_t0 = Context.get_single_context(turns, CONTEXT_LENGTH)
            transition = Transition(s0, a0, context_t0, s1, a1, context_t1)
            transitions.append(transition)
        if len(transitions) < BATCH_SIZE:
            return None

        assert len(transitions) == BATCH_SIZE

        actions = [transition.action_t0 for transition in transitions]
        states = numpy.array([transition.state_t0.as_vector() for transition in transitions])
        contexts = numpy.array([transition.context_t0.as_matrix() for transition in transitions])
        future_states = numpy.array([transition.state_t1.as_vector() for transition in transitions])
        future_contexts = numpy.array([transition.context_t1.as_matrix() for transition in transitions])
        terminals = numpy.array([0 if transition.terminal else 1 for transition in transitions])
        rewards = numpy.array([transition.action_t0.reward for transition in transitions])

        assert future_states.shape == (BATCH_SIZE,) + STATE_SHAPE
        assert contexts.shape == (BATCH_SIZE,) + CONTEXT_SHAPE
        assert rewards.shape == (BATCH_SIZE,)

        target_quality = self._target.predict({
            'state_input': future_states,
            'context_input': future_contexts
        })
        assert target_quality.shape == (BATCH_SIZE, NUM_ACTIONS)
        quality_batch = target_quality.max(axis=1).flatten()
        quality_batch *= self.discount
        quality_batch *= terminals
        logger.debug("Future qualities are {}".format(quality_batch))
        logger.debug('Rewards are {}'.format(rewards))
        quality_batch = rewards + quality_batch

        logger.debug("Working with qualities {}".format(quality_batch))

        target_quality = numpy.zeros((BATCH_SIZE, NUM_ACTIONS))
        for target, action, quality in zip(target_quality, actions, quality_batch):
            target[action.intent_index] = quality

        return (
            {'state_input': states, 'context_input': contexts},
            {'quality_output': target_quality}
        )

    def _prediction_to_action(self, prediction: numpy.ndarray) -> str:
        prediction = prediction[0]
        return ACTIONS[prediction.argmax()]
