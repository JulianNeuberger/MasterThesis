import logging
from pickle import dump, load

import numpy
from keras.utils import to_categorical

from bot.config import *
from turns.models import Sentence, UserProfile

logger = logging.getLogger('data')


def get_raw():
    sentences = Sentence.objects.order_by('said_in', 'said_on').all()
    turns = list_to_pairs(sentences)
    xs = []
    ys = []
    for turn in turns:
        try:
            x, y = process_turn(turn)
            xs.append(x)
            ys.append(y)
        except TurnNotUsable:
            logger.info('Turn "{}" -> "{}" can not be used, see warnings above, skipping it.'.format(turn[0], turn[1]))
    return xs, ys


def list_to_pairs(input_list):
    return zip(input_list[::2], input_list[1::2])


def process_turn(turn):
    user_sentence, bot_sentence = turn
    try:
        x = state_from_sentence(user_sentence)
    except NoStateIntentError as intent_error:
        logger.error('Intent "{}" can not be in a state.'.format(intent_error.intent.template.name))
        raise TurnNotUsable

    try:
        y = action_from_sentence(bot_sentence)
    except NoIntentError:
        logger.error('Bot produced sentence "{}" has no intent, you should add one to cover it!'.format(bot_sentence))
        raise TurnNotUsable
    except NoActionIntentError as intent_error:
        logger.error('Intent "{}" is not a action.'.format(intent_error.intent.template.name))
        raise TurnNotUsable
    return x, y


def state_from_sentence(sentence: Sentence):
    if sentence.intent is None:
        intent_name = 'common.unknown'
    else:
        intent_name = sentence.intent.template.name
    if intent_name not in INTENTS:
        raise NoStateIntentError(sentence.intent)
    return [
        to_categorical(y=INTENTS.index(intent_name), num_classes=NUM_INTENTS),
        sentence.sentiment,
        convert_user_profile(sentence.user_profile)
    ]


def action_from_sentence(sentence: Sentence):
    if sentence.intent is None:
        raise NoIntentError
    if sentence.intent.template.name not in ACTIONS:
        raise NoActionIntentError(sentence.intent)
    return [to_categorical(y=ACTIONS.index(sentence.intent.template.name), num_classes=NUM_ACTIONS)]


def convert_user_profile(user_profile: UserProfile):
    user_profile = [user_profile.name,
                    user_profile.age,
                    user_profile.has_favourite_player,
                    user_profile.has_favourite_team,
                    user_profile.is_active_player]
    return [1 if x is not None else 0 for x in user_profile]


def pre_process(xs, ys):
    xs, ys = numpy.array(xs), numpy.array(ys)
    split = int(xs.shape[0] * (1 - TEST_RATIO))
    permutation = numpy.random.permutation(xs.shape[0])
    train_indices, test_indices = permutation[:split], permutation[split:]
    return (xs[train_indices], ys[train_indices]), (xs[test_indices], ys[test_indices])


def load_dumped():
    with open('data.dump', mode='rb') as file:
        return load(file)


def dump_pre_processed(pre_processed_data):
    with open('data.dump', mode='wb') as file:
        dump(pre_processed_data, file)


class NoIntentError(Exception):
    pass


class IntentError(Exception):
    def __init__(self, intent):
        super().__init__()
        self.intent = intent


class NoStateIntentError(IntentError):
    pass


class NoActionIntentError(IntentError):
    pass


class TurnNotUsable(Exception):
    pass


if __name__ == '__main__':
    logger.info('Started pre processing of data...')
    xs, ys = get_raw()
    processed = pre_process(xs, ys)
    dump_pre_processed(processed)
    logger.info('Finished pre processing data!')
