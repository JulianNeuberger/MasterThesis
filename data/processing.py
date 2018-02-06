import logging
from pickle import dump, load

import numpy
from django.contrib.auth.models import User

from bot.config import TEST_RATIO, CONTEXT_LENGTH
from data.turn import Turn
from turns.models import Sentence
from turns.transition import Transition

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
    bot_user = User.object.get(username='Chatbot')
    turns = Turn.sentences_to_turns(sentences, bot_user)
    transitions = Transition.all_transitions_from_turns(turns, CONTEXT_LENGTH)
    transitions = numpy.array(transitions)
    transitions = test_train_split_numpy_array(transitions)
    dump_data(transitions)
