from typing import List, Tuple

import numpy
from numpy.core.multiarray import ndarray

from bot.config import CONTEXT_LENGTH
from data.action import Action
from data.context import Context
from data.state import State
from data.turn import Turn


class Transition:
    TURNS_FOR_CONVERSION = 2
    SENTENCES_FOR_CONVERSION = TURNS_FOR_CONVERSION * 2

    def __init__(self, state_t0: State, action_t0: Action, context_t0: Context, state_t1: State):
        self.state_t0 = state_t0
        self.state_t1 = state_t1
        self.action_t0 = action_t0
        self.context_t0 = context_t0

    @staticmethod
    def transitions_to_data(transitions: List["Transition"], model):
        states = []
        contexts = []
        qualities = []
        for transition in transitions:
            state, context, quality = transition.to_data_tuple(model)
            states.append(state)
            contexts.append(context)
            qualities.append(quality)
        return numpy.array(states), numpy.array(contexts), numpy.array(qualities)

    def to_data_tuple(self, model) -> Tuple[ndarray, ndarray, ndarray]:
        """
        converts this transition to a tuple of numpy arrays containing the data, that makes up this transition
        :param model: a queryable model, that approximates the quality function
        :return: a tuple of 3 numpy arrays: state, context and quality
        """
        return (
            self.state_t0.as_vector(),
            self.context_t0.as_matrix(),
            self.action_t0.to_quality_vector(model, self.state_t0, self.context_t0, self.state_t1))

    @staticmethod
    def single_transition_from_turns(turns: List[Turn], context_length=CONTEXT_LENGTH):
        assert len(turns) >= 2, 'You need at least 2 turns for a Transition (= s_0->s_1 with no context)'
        final_turn = turns[-1]
        current_turn = turns[-2]
        context = Context.get_single_context(turns[:-2], context_length)
        transition = Transition(current_turn.user, current_turn.bot, context, final_turn.user)
        return transition

    @staticmethod
    def all_transitions_from_turns(turns: List[Turn], context_length=CONTEXT_LENGTH):
        transitions = []
        num_turns = len(turns)
        turns = turns[::-1]
        # one slice needs to have context_length turns for the context
        # and one for each State s_0 (current state) as well as State s_1 (future state)
        slice_size = context_length + 2
        for i, turn in enumerate(turns):
            remaining_turns = min(num_turns - i, slice_size)
            turns_slice = turns[i:i + remaining_turns]
            if len(turns_slice) >= 2:
                # need at least 2 states for a proper transition
                transition = Transition.single_transition_from_turns(turns_slice, context_length)
                transitions.append(transition)
        return transitions