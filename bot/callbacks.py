import logging

from keras.callbacks import Callback
from keras.engine import Model

from bot.config import START_DISCOUNT, END_DISCOUNT, END_DISCOUNT_EPISODES, START_EPSILON, RESET_EPISODES, EPSILON_DECAY

logger = logging.getLogger("bot")


class OvertimeParameterCallback(Callback):
    def __init__(self, start):
        super().__init__()
        self._start = start
        self._current_step = 0
        self._value = self._start

    def _update_value(self):
        raise NotImplementedError('You have to implement the _update_values function for an OvertimeParameterCallback')

    def on_batch_end(self, batch, logs=None):
        super().on_batch_end(batch, logs)
        self._current_step += 1
        self._update_value()

    @property
    def value(self):
        return self._value


class EpsilonCallback(OvertimeParameterCallback):
    def __init__(self):
        super().__init__(START_EPSILON)

    def _update_value(self):
        prev_value = self._value
        self._value = self._value / EPSILON_DECAY
        logger.debug('Updating epsilon for batch #{}, it is now {} (was {})'
                     .format(self._current_step, self._value, prev_value))


class DiscountCallback(OvertimeParameterCallback):
    def __init__(self):
        super().__init__(START_DISCOUNT)
        self._end = END_DISCOUNT
        self._end_steps = END_DISCOUNT_EPISODES

    def _update_value(self):
        prev_value = self._value
        if self._value > self._end:
            self._value = self._start - ((self._start - self._end) / self._end_steps) * self._current_step
            self._value = max(self._value, self._end)
            logger.debug('Updating discount for batch #{}, it is now {} (was {})'
                         .format(self._current_step, self._value, prev_value))


class TargetResetCallback(Callback):
    def __init__(self, model: Model, target: Model, reset_episodes: int = RESET_EPISODES):
        super().__init__()
        self._epochs_seen = 0
        self._reset_episodes = reset_episodes
        self._target = target
        self._model = model

    def on_epoch_end(self, epoch, logs=None):
        self._epochs_seen += 1
        if self._epochs_seen % self._reset_episodes == 0:
            logger.info('Resetting the target function...')
            self._target.set_weights(self._model.weights)
