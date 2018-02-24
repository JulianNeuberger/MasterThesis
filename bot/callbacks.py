import logging

from keras.callbacks import Callback
from keras.engine import Model

from bot.config import START_DISCOUNT, END_DISCOUNT, END_DISCOUNT_BATCHES, START_EPSILON, EPSILON_DECAY

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
        self._value = self._value / EPSILON_DECAY

    def on_epoch_end(self, epoch, logs=None):
        logger.debug('Epsilon is now {:.6}'.format(self._value))


class DiscountCallback(OvertimeParameterCallback):
    def __init__(self):
        super().__init__(START_DISCOUNT)
        self._end = END_DISCOUNT
        self._end_steps = END_DISCOUNT_BATCHES

    def _update_value(self):
        if self._value > self._end:
            self._value = self._start - ((self._start - self._end) / self._end_steps) * self._current_step
            self._value = max(self._value, self._end)

    def on_epoch_end(self, epoch, logs=None):
        logger.debug('Discount is now {:.6}'.format(self._value))


class TargetResetCallback(Callback):
    def __init__(self, model: Model, target: Model):
        super().__init__()
        self._epochs_seen = 0
        self._target = target
        self._model = model

    def on_epoch_end(self, epoch, logs=None):
        self._epochs_seen += 1
        logger.info('Resetting the target function...')
        self._target.set_weights(self._model.get_weights())
