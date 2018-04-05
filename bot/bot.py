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
from bot.exceptions import NoDataException
from bot.neural_nets import get_deep_mind_model
from data.action import Action
from data.context import Context
from data.exceptions import IntentError
from data.state import State
from data.transition import Transition
from data.turn import Turn
from turns.models import Sentence
from config.models import Configuration

logger = logging.getLogger("bot")


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class AbstractBot(metaclass=Singleton):
    """
    A Singleton, that holds a keras model and can be trained, be queried and predict actions.
    The core of the chat bot.
    Extend this class to use your models and logic.
    """

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # ABSTRACT METHODS                                                         #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def _init_model(self, *args, **kwargs):
        """
        Initializes the underlying keras model used by this QueryableModel.
        Implementation should set the self._model member and is mandatory.
        Can be called multiple times, to change model implementation

        This method is not responsible for:
        - loading model stats (episodes trained, ...)
        - loading model weights
        """
        raise NotImplementedError

    def _sample_batch(self, episode_number) -> Optional[Tuple[int, Dict, Dict]]:
        """
        Method for sampling one batch to use in training.
        Can return None, if training not possible.
        Method is responsible for ordering/shuffling samples.

        Implement this method!

        :parameter episode_number: Episode to sample a batch from, 0 is the first episode of data,
        each episode consists of Configuration.episode_size sentences. pass negative integers to indicate the
        last (-1), second last (-2) and so on episodes

        :return: a tuple of batch size and dicts of input and output batch
        """
        raise NotImplementedError()

    def _can_sample_batch(self, episode_number) -> bool:
        """"""
        raise NotImplementedError()

    def _prediction_to_action_name(self, prediction: numpy.ndarray) -> str:
        """
        Implement this to process a raw model prediction into an action name

        :param prediction: a 1D numpy array resulting from querying the model (2nd dimension squeezed)

        :returns: a action name string
        """
        raise NotImplementedError()

    def __init__(self, model_base_name: str, load_dir='latest'):
        """
        Gets/Creates a QueryableModel (singleton!).
        Initializes the keras.model and Discount/EpsilonCallbacks

        :param model_base_name: base name of that model (e.g. "deep_mind_model")
        :param load_dir: path to weights to be loaded from. Defaults to latest,
            which loads the latest model with that basename, use None for a "fresh" model
        """
        self._training_lock = Lock()

        self._callbacks = []
        self._model = None
        self._stats = {
            'episodes_seen': 0,
            'samples_seen': 0
        }
        self._graph = tf.get_default_graph()

        self._model_base_name = model_base_name
        self._init_model(load_dir)
        assert self._model is not None, 'Method _init_model has to set _model member!'
        self._init_callbacks()
        for callback in self._callbacks:
            callback.set_model(self._model)

        self._init_directories()

        if load_dir:
            if os.path.isfile(self.model_weight_file):
                logger.info('Loading model weights from "{}".'.format(self.model_weight_file))

                self._load_stats()
                self._on_stats_loaded()

                self._model.load_weights(self.model_weight_file)
                self._on_weights_loaded()
            else:
                logger.info('No weights file for model "{}" found, '
                            'this can be due to the first time running this model...'.format(self._model.name))

    def _init_callbacks(self):
        """
        Initializes callbacks needed for this model.
        Implement to specify callbacks used.
        Defaults to using only TensorBoard callback.
        """
        self._callbacks = [TensorBoard(log_dir=os.path.join(Configuration.get_active().log_dir, self._model.name))]

    def _on_weights_loaded(self):
        """
        Override this, to implement behaviour, when the weights file is found and model loaded the weights
        Use self.model_weights_file property to get the filename
        """
        pass

    def _on_stats_loaded(self):
        """
        Override this, to implement behaviour, when the stats file is found and loaded
        Use self.model_stats_file property to get the filename
        """
        pass

    def predict(self, inputs: Dict[str, numpy.ndarray]):
        """
        Simple delegate for the keras.model.predict function

        :param inputs: input as dict of input_name->numpy.ndarray
        :return: an array of quality vectors for each input row (state/context pair), not processed,
                    see keras.model.predict
        """
        with self._graph.as_default():
            return self._model.predict(inputs, batch_size=Configuration.get_active().batch_size)

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
            return self._prediction_to_action_name(self._model.predict(raw_input))

    def pre_train(self, validate=True):
        logger.info('Starting to train on available episodes.')
        episodes_trained = 0
        while self.train(validate):
            episodes_trained += 1
            pass
        logger.info('Successfully trained on {} episodes.'.format(episodes_trained))

    def train(self, validate=True):
        """Trains for a single episode

        :return: a bool indicating whether or not training was possible and successful.
        """
        logger.debug('Acquiring lock...')
        with self._training_lock:
            if not self._can_sample_batch(self.episodes_seen):
                logger.debug('No more episodes to train on are available!')
                return False
            with self._graph.as_default():
                episode_logs = {}
                training_loss = 0
                batches_trained = 0
                logger.info('Bot training on episode #{}'.format(self.episodes_seen))
                for step in range(0, Configuration.get_active().steps_per_episode):
                    num_samples, x, y = self._sample_batch(self.episodes_seen)
                    if num_samples > 0:
                        loss = self._perform_training_step((x, y))
                        batch_logs = {'loss': loss}
                        self._on_batch_end(batches_trained, batch_logs)
                        training_loss += batch_logs['loss']
                        batches_trained += 1
                        self.samples_seen += num_samples
                    else:
                        return False
                training_loss /= batches_trained
                episode_logs['loss'] = training_loss
                if validate:
                    num_samples, x, y = self._sample_batch(self.episodes_seen)
                    if num_samples > 0:
                        episode_logs['val_loss'] = self._model.test_on_batch(x, y)
                self.episodes_seen += 1
                self._save_stats()
                self._save_weights()
                self._on_episode_end(self.episodes_seen, episode_logs)
                return True

    def save_weights(self):
        with self._graph.as_default():
            self._backup_weights()
            self._save_weights()
            return True

    def is_training(self):
        return self._training_lock.locked()

    def is_saving(self):
        return False

    @staticmethod
    def list_available_models():
        models = []
        for name in os.listdir(Configuration.get_active().weights_dir):
            stats = AbstractBot._load_stats_by_path(
                os.path.join(Configuration.get_active().weights_dir, name, 'stats.pickle'))
            model = (name, stats)
            models.append(model)
        return models

    def _perform_training_step(self, batch):
        x, y = batch
        return self._model.train_on_batch(x, y)

    def _on_batch_end(self, batch_number, logs):
        for callback in self._callbacks:
            callback.on_batch_end(batch_number, logs)

    def _on_episode_end(self, episode_number, logs):
        logger.debug('Episode ended, notifying callbacks {}'.format(self._callbacks))
        for callback in self._callbacks:
            callback.on_epoch_end(episode_number, logs)

    def _backup_weights(self):
        logger.info('Backing up weight file...')
        if not os.path.exists(self.model_directory):
            os.makedirs(self.model_directory)
        if os.path.isfile(self.model_weight_file):
            copyfile(self.model_weight_file, self.model_weight_backup)
            logger.info('Successfully backed up weights.')

    def _init_directories(self):
        os.makedirs(self.model_directory, exist_ok=True)

    def _save_weights(self):
        logger.info('Saving current weights...')
        self._model.save_weights(self.model_weight_file)
        logger.info('Successfully saved weights.')

    def _load_stats(self):
        self._stats = AbstractBot._load_stats_by_path(self.model_stats_file)

    @staticmethod
    def _load_stats_by_path(path):
        if os.path.isfile(path):
            with open(path, 'rb') as file:
                return pickle.load(file)
        else:
            return AbstractBot._get_empty_stats()

    @staticmethod
    def _get_empty_stats():
        return {
            'episodes_seen': 0,
            'samples_seen': 0
        }

    def _save_stats(self):
        logger.info('Writing model stats...')
        with open(self.model_stats_file, 'wb') as stats_file:
            pickle.dump(self._stats, stats_file)
        logger.info('Successfully wrote stats.')

    @property
    def episodes_seen(self):
        return self._stats['episodes_seen']

    @episodes_seen.setter
    def episodes_seen(self, value):
        assert value >= 0
        self._stats['episodes_seen'] = value

    @property
    def samples_seen(self):
        return self._stats['samples_seen']

    @samples_seen.setter
    def samples_seen(self, value):
        assert value >= 0
        self._stats['samples_seen'] = value

    @property
    def model_directory(self):
        return os.path.join(Configuration.get_active().weights_dir, self._model.name)

    @property
    def model_weight_file(self):
        return os.path.join(self.model_directory, 'weights.pickle')

    @property
    def model_weight_backup(self):
        return os.path.join(self.model_directory, 'weights.pickle.bkp')

    @property
    def model_stats_file(self):
        return os.path.join(self.model_directory, 'stats.pickle')

    @staticmethod
    def _write_log(callback, names, logs, batch_no):
        for name, value in zip(names, logs):
            logger.debug('Writing logs for callback {}.'.format(type(callback).__name__))
            summary = tf.Summary()
            summary_value = summary.value.add()
            summary_value.simple_value = value
            summary_value.tag = name
            callback.writer.add_summary(summary, batch_no)
            callback.writer.flush()


class DeepMindBot(AbstractBot):
    def __init__(self, bot_user, load_dir=None):
        super().__init__(model_base_name='deep_mind_model', load_dir=load_dir)
        self._bot_user = bot_user

    def _init_model(self, load_model_dir=None):
        """
        Initializes a DeepMind inspired model. Use the load_model_dir parameter to load a previously
        trained model.

        :param load_model_dir: directory of a previously trained and saved model, leave None if you want a fresh one
         use 'latest' for the last trained model with the given base name
        """
        if not os.path.isdir(Configuration.get_active().log_dir):
            os.makedirs(Configuration.get_active().log_dir)
        num_models = len([name for name in os.listdir(Configuration.get_active().log_dir) if
                          os.path.isdir(os.path.join(Configuration.get_active().log_dir,
                                                     name)) and self._model_base_name in name])
        if load_model_dir == 'latest':
            model_number = num_models - 1
            model_name = '{}_v{:03d}'.format(self._model_base_name, model_number)
        elif load_model_dir is None:
            model_number = num_models
            model_name = '{}_v{:03d}'.format(self._model_base_name, model_number)
        else:
            model_name = load_model_dir
        self._model = get_deep_mind_model(name=model_name)
        self._target = get_deep_mind_model()

        # init target weights
        self._target.set_weights(self._model.get_weights())

    def _init_callbacks(self):
        self._discount_callback = DiscountCallback()
        self._epsilon_callback = EpsilonCallback()
        super()._init_callbacks()
        self._callbacks.extend([
            self._epsilon_callback,
            self._discount_callback,
            TargetResetCallback(self._model, self._target)
        ])

    def _on_weights_loaded(self):
        self._target.load_weights(self.model_weight_file)

    @property
    def discount(self):
        return self._discount_callback.value

    @property
    def epsilon(self):
        return self._epsilon_callback.value

    def _sample_batch(self, episode_number) -> Tuple[int, Dict, Dict]:
        start, stop = DeepMindBot._episode_to_range(episode_number)
        sentences = \
            [Sentence.sample_sentence_in_range(self._bot_user.username, start, stop) for _ in
             range(0, Configuration.get_active().batch_size)]
        transitions = []
        for sentence in sentences:
            context_sentences = []
            while len(context_sentences) < 4:
                assert sentence.said_by == self._bot_user.username
                context_sentences = Sentence.objects.filter(
                    said_in=sentence.said_in
                ).filter(
                    said_on__lte=sentence.said_on
                ).order_by(
                    '-said_on'
                )[:Configuration.get_active().context_length * 2 + 4]
                context_sentences = list(reversed(context_sentences))
                if len(context_sentences) < 4:
                    # re-sample, since this sample has not enough context
                    sentence = Sentence.sample_sentence_in_range(self._bot_user.username, start, stop)
            try:
                a1 = Action(context_sentences.pop())
                s1 = State(context_sentences.pop())
                turns = Turn.sentences_to_turns(context_sentences, self._bot_user)
                # context turns list should only be CONTEXT_LENGTH long
                raw_context_t1 = turns[0:Configuration.get_active().context_length]
                context_t1 = Context.get_single_context(raw_context_t1, Configuration.get_active().context_length)

                a0 = Action(context_sentences.pop())
                s0 = State(context_sentences.pop())
                turns = Turn.sentences_to_turns(context_sentences, self._bot_user)
                context_t0 = Context.get_single_context(turns, Configuration.get_active().context_length)
            except IntentError as e:
                logger.error('Error occurred while processing sampled sentence {}. See below.'.format(sentence))
                raise e

            transition = Transition(s0, a0, context_t0, s1, a1, context_t1)
            transitions.append(transition)
        if len(transitions) < Configuration.get_active().batch_size:
            return 0, {}, {}

        assert len(transitions) == Configuration.get_active().batch_size

        actions = [transition.action_t0 for transition in transitions]
        states = numpy.array([transition.state_t0.as_vector() for transition in transitions])
        contexts = numpy.array([transition.context_t0.as_matrix() for transition in transitions])
        future_states = numpy.array([transition.state_t1.as_vector() for transition in transitions])
        future_contexts = numpy.array([transition.context_t1.as_matrix() for transition in transitions])
        terminals = numpy.array([0 if transition.terminal else 1 for transition in transitions])
        rewards = numpy.array([transition.action_t0.reward for transition in transitions])

        assert future_states.shape == (Configuration.get_active().batch_size,) + Configuration.get_active().state_shape
        assert contexts.shape == (Configuration.get_active().batch_size,) + Configuration.get_active().context_shape
        assert rewards.shape == (Configuration.get_active().batch_size,)

        target_quality = self._target.predict({
            'state_input': future_states,
            'context_input': future_contexts
        })
        assert target_quality.shape == (
            Configuration.get_active().batch_size, Configuration.get_active().number_actions
        )
        quality_batch = target_quality.max(axis=1).flatten()
        quality_batch *= self.discount
        quality_batch *= terminals
        logger.debug("Future qualities are {}".format(quality_batch))
        logger.debug('Rewards are {}'.format(rewards))
        quality_batch = rewards + quality_batch

        logger.debug("Working with qualities {}".format(quality_batch))

        target_quality = numpy.zeros((Configuration.get_active().batch_size, Configuration.get_active().number_actions))
        for target, action, quality in zip(target_quality, actions, quality_batch):
            target[action.intent_index] = quality

        return (
            len(states),
            {'state_input': states, 'context_input': contexts},
            {'quality_output': target_quality}
        )

    def _can_sample_batch(self, episode_number) -> bool:
        start, stop = DeepMindBot._episode_to_range(episode_number)
        try:
            return Sentence.has_episode(start, stop)
        except NoDataException:
            return False

    @staticmethod
    def _episode_to_range(episode_number) -> Tuple[int, int]:
        num_sentences = Sentence.objects.count()
        if num_sentences == 0:
            raise NoDataException
        start = episode_number * Configuration.get_active().episode_size
        end = (episode_number + 1) * Configuration.get_active().episode_size
        if episode_number < 0:
            start += num_sentences
            end += num_sentences
        return start, end

    def _prediction_to_action_name(self, prediction: numpy.ndarray) -> str:
        prediction = prediction[0]
        return list(Configuration.get_active().action_intents.all())[prediction.argmax()].name
