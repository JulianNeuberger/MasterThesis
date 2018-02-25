from random import randint

from bot.config import ACTION_SENTENCES


def response_for_action(action_name):
    possible_responses = ACTION_SENTENCES[action_name]
    rand_index = randint(0, len(possible_responses) - 1)
    return possible_responses[rand_index]
