import logging
from pickle import dump, load

import numpy

from bot.config import TEST_RATIO
from data.context import Context
from data.turn import Turn
from turns.models import Sentence

logger = logging.getLogger('data')


def test_train_split_numpy_array(array):
    split = int(array.shape[0] * (1 - TEST_RATIO))
    permutation = numpy.random.permutation(array.shape[0])
    train_indices, test_indices = permutation[:split], permutation[split:]
    return array[train_indices], array[test_indices]


def load_dumped():
    with open('data.dump', mode='rb') as file:
        return load(file)


def dump_data(data):
    with open('data.dump', mode='wb') as file:
        dump(data, file)


def run_pre_processing():
    sentences = Sentence.objects.order_by('said_in', 'said_on').all()
    logger.info('Pre processing {} sentences'.format(len(sentences)))
    turns = Turn.sentences_to_turns(sentences)
    contexts = Context.get_contexts_from_turns(turns)
    # contexts = [context.as_matrix() for context in contexts]
    contexts = numpy.array(contexts)
    contexts = test_train_split_numpy_array(contexts)
    dump_data(contexts)
