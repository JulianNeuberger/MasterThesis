import os
from typing import Iterable

from bot.config import IMAGINATION_MODEL_LATEST_WEIGHTS_FILE
from bot.model import get_imagination_model
from bot.training import predict, train_on_contexts
from data.context import Context
from data.state import State
from events.util import Singleton


class QueryableModel(metaclass=Singleton):
    def __init__(self):
        self._model = get_imagination_model()
        if os.path.isfile(IMAGINATION_MODEL_LATEST_WEIGHTS_FILE):
            self._model.load_weights(IMAGINATION_MODEL_LATEST_WEIGHTS_FILE)

    def query(self, states: Iterable[State], contexts: Iterable[Context]):
        return predict(self._model, states, contexts)

    def train(self, contexts):
        train_on_contexts(self._model, contexts)
