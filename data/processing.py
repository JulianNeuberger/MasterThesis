import logging
from pickle import dump, load
from typing import Tuple, List

import numpy
from keras.utils import to_categorical

from bot.config import *
from turns.models import Sentence, UserProfile

logger = logging.getLogger('data')


def get_transitions():
    sentences = Sentence.objects.order_by('said_in', 'said_on').all()
    logger.info('Pre processing {} sentences'.format(len(sentences)))
    turns = list_to_pairs(sentences)
    num_turns = len(turns)
    transitions = []
    for i, turn in enumerate(turns):
        try:
            if i < (num_turns - 1):
                # is there a next turn after this one?
                next_turn = turns[i + 1]
                if next_turn[0].said_in == turn[0].said_in:
                    # same conversation?
                    transition = process_turn(turn, next_turn)
                    transitions.append(transition)
        except TurnNotUsable:
            logger.warning(
                'Turn "{}" -> "{}" can not be used, see warnings above, skipping it.'.format(turn[0], turn[1]))
    return transitions


def list_to_pairs(input_list):
    return list(zip(input_list[::2], input_list[1::2]))


def process_turn(turn, later_turn):
    transition = Transition(turn, later_turn)
    return transition


def state_from_sentence(sentence: Sentence):
    if sentence.intent is None:
        intent_name = 'common.unknown'
    else:
        intent_name = sentence.intent.template.name
    if intent_name not in INTENTS:
        raise NoStateIntentError(sentence.intent)
    state = to_categorical(y=INTENTS.index(intent_name), num_classes=NUM_INTENTS)
    state = numpy.append(state, [float(sentence.sentiment)])
    state = numpy.append(state, convert_user_profile(sentence.user_profile))
    return state


def action_from_sentence(sentence: Sentence):
    if sentence.intent is None:
        raise NoIntentError(sentence)
    if sentence.intent.template.name not in ACTIONS:
        raise NoActionIntentError(sentence.intent)
    return to_categorical(y=ACTIONS.index(sentence.intent.template.name), num_classes=NUM_ACTIONS)[0]


def convert_user_profile(user_profile: UserProfile):
    user_profile = [user_profile.name,
                    user_profile.age,
                    user_profile.has_favourite_player,
                    user_profile.has_favourite_team,
                    user_profile.is_active_player]
    return [1 if x is not None else 0 for x in user_profile]


def pre_process_transitions(transitions):
    transitions = numpy.array(transitions)
    contexts = []
    for i, transition in enumerate(transitions):
        context = []
        for j in range(0, CONTEXT_LENGTH):
            if i - j >= 0:
                context.append(transitions[i - j])
        context = pad_context(context, CONTEXT_LENGTH)
        contexts.append(context)
    contexts = numpy.array(contexts)
    split = int(contexts.shape[0] * (1 - TEST_RATIO))
    permutation = numpy.random.permutation(contexts.shape[0])
    train_indices, test_indices = permutation[:split], permutation[split:]
    return contexts[train_indices], contexts[test_indices]


def pad_context(context: List, pad_to_length: int):
    if len(context) < pad_to_length:
        missing = pad_to_length - len(context)
        padding = [None] * missing
        context = context + padding
    return context


def load_dumped():
    with open('data.dump', mode='rb') as file:
        return load(file)


def dump_pre_processed_transitions(pre_processed_data):
    with open('data.dump', mode='wb') as file:
        dump(pre_processed_data, file)


class Transition:
    def __init__(self, start_turn: Tuple[Sentence, Sentence], next_turn: Tuple[Sentence, Sentence]):
        logger.debug('Trying to create Transition from turns "{}" -> "{}", "{}" -> "{}"'.format(
            start_turn[0],
            start_turn[1],
            next_turn[0],
            next_turn[1]
        ))
        start_user, start_bot = start_turn
        next_user, next_bot = next_turn
        try:
            self.state = state_from_sentence(start_user)
            self.next_state = state_from_sentence(next_user)
            self.action = action_from_sentence(start_bot)
            self.reward = float(next_user.reward)
            self.terminal = bool(next_bot.terminal)
        except NoIntentError or IntentError or NoStateIntentError:
            raise TurnNotUsable
        except NoIntentError as e:
            logger.error('Bot produced sentence "{}" has no intent, you should add one to cover it!'.format(
                e.sentence
            ))
        except NoStateIntentError as e:
            logger.error('Intent "{}" can not be in a state.'.format(e.intent.template.name))
            raise TurnNotUsable
        except NoActionIntentError as e:
            logger.error('Intent "{}" is not a action.'.format(e.intent.template.name))
            raise TurnNotUsable

    def get_quality(self, model, discount=DISCOUNT):
        state = self.state
        state = numpy.array([self.state])
        qualities = model.predict(state)[0]
        action_index = numpy.argmax(self.action)
        if self.terminal is True:
            # this is the last action in the sequence, do not use discounting
            qualities[action_index] = self.reward
        else:
            next_state = self.next_state
            next_state = numpy.array([next_state])
            future_value = model.predict(next_state)[0]
            # in the middle of a sequence, use discounting
            qualities[action_index] = self.reward + discount * numpy.max(future_value)
        return qualities


class NoIntentError(Exception):
    def __init__(self, sentence):
        self.sentence = sentence


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


def run_pre_processing():
    transitions = get_transitions()
    transitions = pre_process_transitions(transitions)
    dump_pre_processed_transitions(transitions)


if __name__ == '__main__':
    logger.info('Started pre processing of data...')
    run_pre_processing()
    logger.info('Finished pre processing data!')
