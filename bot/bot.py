import logging
import os
import pickle
from shutil import copyfile
from threading import Lock
from typing import Dict, Optional, Tuple

import numpy
import tensorflow as tf
from keras.callbacks import TensorBoard

from bot.callbacks import DiscountCallback, EpsilonCallback, TargetResetCallback
from bot.config import BATCH_SIZE, ACTIONS, LOG_DIR, WEIGHTS_DIR, CONTEXT_LENGTH, NUM_ACTIONS, \
    STATE_SHAPE, CONTEXT_SHAPE, EPISODE_SIZE, STEPS_PER_EPISODE
from bot.exceptions import NoDataException
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
        self._training_lock = Lock()

        self._callbacks = []
        self._model = None
        self._episodes_seen = 0
        self._graph = tf.get_default_graph()

        self._model_base_name = model_name

        self._init_model(load)
        assert self._model is not None, 'Method _init_model has to set _model member!'
        self._init_callbacks()
        for callback in self._callbacks:
            callback.set_model(self._model)

        self._init_directories()
        self._load_stats()

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

    def pre_train(self, validate=True):
        while self.train(validate):
            pass

    def train(self, validate=True):
        with self._training_lock:
            if not self._can_sample_batch(self._episodes_seen):
                return False
            with self._graph.as_default():
                episode_logs = {}
                training_loss = 0
                batches_trained = 0
                logger.info('Bot training on episode #{}'.format(self._episodes_seen))
                for step in range(0, STEPS_PER_EPISODE):
                    batch = self._sample_batch(self._episodes_seen)
                    if batch is not None:
                        loss = self._perform_training_step(batch)
                        batch_logs = {'loss': loss}
                        self._on_batch_end(batches_trained, batch_logs)
                        training_loss += batch_logs['loss']
                        batches_trained += 1
                    else:
                        return False
                training_loss /= batches_trained
                episode_logs['loss'] = training_loss
                if validate:
                    batch = self._sample_batch(self._episodes_seen)
                    if batch is not None:
                        x, y = batch
                        episode_logs['val_loss'] = self._model.test_on_batch(x, y)
                self._on_episode_end(self._episodes_seen, episode_logs)
                self._episodes_seen += 1
                self._save_stats()
                return True

    def save_weights(self):
        with self._graph.as_default():
            self._backup_weights()
            self._save_weights()

    def is_training(self):
        return self._training_lock.locked()

    def is_saving(self):
        return False

    def _perform_training_step(self, batch):
        x, y = batch
        return self._model.train_on_batch(x, y)

    def _on_batch_end(self, batch_number, logs):
        for callback in self._callbacks:
            callback.on_batch_end(batch_number, logs)

    def _on_episode_end(self, episode_number, logs):
        for callback in self._callbacks:
            if hasattr(callback, 'writer'):
                QueryableModelInterface._write_log(callback, ['loss', 'val_loss'], logs.values(), episode_number)
            callback.on_epoch_end(episode_number, logs)

    def _sample_batch(self, episode_number) -> Optional[Tuple[Dict, Dict]]:
        """
        Method for sampling one batch to use in training.
        Can return None, if training not possible.
        Method is responsible for ordering/shuffling samples.

        Implement this method!

        :parameter episode_number: Episode to sample a batch from, 0 is the first episode of data,
        each episode consists of bot.config.EPISODE_SIZE sentences. pass negative integers to indicate the
        last (-1), second last (-2) and so on episodes

        :return: None, if no training possible, a tuple of dicts of input and output batch otherwise
        """
        raise NotImplementedError()

    def _can_sample_batch(self, episode_number) -> bool:
        """"""
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
        if not os.path.exists(self.model_weight_directory):
            os.makedirs(self.model_weight_directory)
        if os.path.isfile(self.model_weight_file):
            copyfile(self.model_weight_file, self.model_weight_backup)
            logger.info('Successfully backed up weights.')

    def _init_directories(self):
        os.makedirs(self.model_weight_directory, exist_ok=True)

    def _save_weights(self):
        logger.info('Saving current weights...')
        self._model.save_weights(self.model_weight_file)
        logger.info('Successfully saved weights.')

    def _load_stats(self):
        if os.path.isfile(self.model_stats_file):
            with open(self.model_stats_file, 'rb') as file:
                stats = pickle.load(file)
            try:
                self._episodes_seen = stats['epochs_trained']
            except KeyError:
                logger.warning('There is a legacy stats file at "{}", overwrite it!'.format(
                    self.model_stats_file
                ))
                self._episodes_seen = stats['steps_seen']
        else:
            self._episodes_seen = 0

    def _save_stats(self):
        logger.info('Writing model stats...')
        stats = {
            'steps_seen': self._episodes_seen
        }
        with open(self.model_stats_file, 'wb') as stats_file:
            pickle.dump(stats, stats_file)
        logger.info('Successfully wrote stats.')

    @property
    def model_weight_directory(self):
        return os.path.join(WEIGHTS_DIR, self._model.name)

    @property
    def model_weight_file(self):
        return os.path.join(self.model_weight_directory, 'weights.pickle')

    @property
    def model_weight_backup(self):
        return os.path.join(self.model_weight_directory, 'weights.pickle.bkp')

    @property
    def model_stats_file(self):
        return os.path.join(self.model_weight_directory, 'stats.pickle')

    @staticmethod
    def _write_log(callback, names, logs, batch_no):
        for name, value in zip(names, logs):
            summary = tf.Summary()
            summary_value = summary.value.add()
            summary_value.simple_value = value
            summary_value.tag = name
            callback.writer.add_summary(summary, batch_no)
            callback.writer.flush()


class DeepMindModel(QueryableModelInterface):
    def __init__(self, bot_user):
        super().__init__('deep_mind_model')
        self._bot_user = bot_user

    def _init_model(self, load=True):
        if not os.path.isdir(LOG_DIR):
            os.makedirs(LOG_DIR)
        num_models = len([name for name in os.listdir(LOG_DIR) if
                          os.path.isdir(os.path.join(LOG_DIR, name)) and self._model_base_name in name])
        model_number = num_models if not load else num_models - 1
        model_name = '{}_v{:03d}'.format(self._model_base_name, model_number)
        self._model = get_deep_mind_model(name=model_name)
        self._target = get_deep_mind_model()
        if load:
            if os.path.isfile(self.model_weight_file):
                logger.info('Loading model weights from "{}".'.format(self.model_weight_file))
                self._model.load_weights(self.model_weight_file)
                self._target.load_weights(self.model_weight_file)
            else:
                logger.info('No weights file for model "{}" found, '
                            'this can be due to the first time running this model...'.format(self._model.name))

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

    def _sample_batch(self, episode_number) -> Optional[Tuple[Dict, Dict]]:
        start, stop = DeepMindModel._episode_to_range(episode_number)
        sentences = \
            [Sentence.sample_sentence_in_range(self._bot_user.username, start, stop) for _ in range(0, BATCH_SIZE)]
        transitions = []
        for sentence in sentences:
            context_sentences = []
            while len(context_sentences) < 4:
                assert sentence.said_by == self._bot_user.username
                context_sentences = Sentence.objects \
                                        .filter(said_in=sentence.said_in).filter(said_on__lte=sentence.said_on) \
                                        .order_by('-said_on')[:CONTEXT_LENGTH * 2 + 4]
                context_sentences = list(reversed(context_sentences))
                # resample, since this sample has not enough context
                sentence = Sentence.sample_sentence_in_range(self._bot_user.username, start, stop)
            a1 = Action(context_sentences.pop())
            s1 = State(context_sentences.pop())
            a0 = Action(context_sentences.pop())
            s0 = State(context_sentences.pop())
            turns = Turn.sentences_to_turns(context_sentences, self._bot_user)
            context_t1 = Context.get_single_context(turns, CONTEXT_LENGTH)
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

    def _can_sample_batch(self, episode_number) -> bool:
        start, stop = DeepMindModel._episode_to_range(episode_number)
        try:
            return Sentence.has_episode(start, stop)
        except NoDataException:
            return False

    @staticmethod
    def _episode_to_range(episode_number) -> Tuple[int, int]:
        num_sentences = Sentence.objects.count()
        if num_sentences == 0:
            raise NoDataException
        start = episode_number * EPISODE_SIZE
        end = (episode_number + 1) * EPISODE_SIZE
        if episode_number < 0:
            start += num_sentences
            end += num_sentences
        return start, end

    def _prediction_to_action(self, prediction: numpy.ndarray) -> str:
        prediction = prediction[0]
        return ACTIONS[prediction.argmax()]
