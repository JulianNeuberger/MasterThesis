import logging

from keras.callbacks import Callback

from bot.config import START_DISCOUNT, END_DISCOUNT, END_DISCOUNT_EPISODES

logger = logging.getLogger("bot")


class DiscountCallback(Callback):
    def __init__(self):
        super().__init__()
        self._discount = START_DISCOUNT
        self._seen_episodes = 0
        self._last_epoch_number = None

    @property
    def discount(self):
        return self._discount

    def on_epoch_end(self, epoch, logs=None):
        super().on_epoch_end(epoch, logs)
        difference = epoch - self._last_epoch_number
        if self._last_epoch_number > epoch:
            # we started anew
            difference = 1
        self._last_epoch_number = epoch
        self._seen_episodes += difference
        prev_discount = self._discount
        self._discount = \
            START_DISCOUNT + ((START_DISCOUNT - END_DISCOUNT) / END_DISCOUNT_EPISODES) * self._seen_episodes
        logger.debug(
            'Updating discount for epoch number {}, it is now {} (was {})'.format(epoch, self._discount, prev_discount))
