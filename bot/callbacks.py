import logging

from keras.callbacks import Callback

from bot.config import START_DISCOUNT, END_DISCOUNT, END_DISCOUNT_EPISODES, START_EPSILON

logger = logging.getLogger("bot")


class OvertimeParameterCallback(Callback):
    def __init__(self, start):
        super().__init__()
        self._start = start
        self._current_step = 0
        self._value = self._start

    def _update_value(self):
        raise NotImplementedError('You have to implement the _update_values function for an OvertimeParameterCallback')

    def on_epoch_end(self, epoch, logs=None):
        super().on_epoch_end(epoch, logs)
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
        self._value = self._value / self._current_step
        logger.debug('Updating epsilon for epoch number {}, it is now {} (was {})'
                     .format(self._current_step, self._value, prev_value))


class DiscountCallback(OvertimeParameterCallback):
    def __init__(self):
        super().__init__(START_DISCOUNT)
        self._end = END_DISCOUNT
        self._end_steps = END_DISCOUNT_EPISODES

    def _update_value(self):
        prev_value = self._value
        self._value = self._start + ((self._start - self._end) / self._end_steps) * self._current_step
        logger.debug('Updating discount for epoch number {}, it is now {} (was {})'
                     .format(self._current_step, self._value, prev_value))
