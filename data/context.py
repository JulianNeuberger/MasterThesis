from typing import List

import numpy

from bot.config import CONTEXT_LENGTH, NUM_ACTIONS, STATE_SHAPE
from data.action import Action
from data.state import State
from data.turn import Turn


class Context:
    _states = None
    _actions = None
    _context_length = 0

    def __init__(self, states: List[State], actions: List[Action], context_length):
        """
        creates a context object from given list of states and actions

        :param states: a list of states to use
        :param actions: a list of actions to use
        :param context_length: number
                of steps into the past, must be greater or equal to number of states/actions provided

        :raises AssertionError: if 1st: number of states/actions is more than the context length or 2nd:
                there are an unequal amount of actions and states provided
        """
        assert len(states) == len(actions)
        assert len(states) <= context_length
        self._states = states
        self._actions = actions

    @property
    def states(self):
        return self._states

    @states.setter
    def states(self, new_states):
        assert len(new_states) <= self._context_length
        self._states = new_states

    @property
    def actions(self):
        return self._actions

    @actions.setter
    def actions(self, actions):
        assert len(actions) <= self._context_length
        self._states = actions

    @property
    def context_length(self):
        return self._context_length

    @context_length.setter
    def context_length(self, new_val):
        if self._actions is not None:
            assert new_val >= len(self._actions)
        if self._states is not None:
            assert new_val >= len(self._states)
        self._context_length = new_val

    def as_matrix(self) -> numpy.array:
        """
        Gets this context in matrix representation.
        Concatenates state and action (in vector form) for each context step

        :return: matrix representation for this context, shape of (CONTEXT_LENGTH, STATE_SHAPE[0]+NUM_ACTIONS)
        """
        # number of missing actions/states
        missing_context = len(self.states) - self.context_length
        ret = []
        for state, action in zip(self.states, self.actions):
            ret.append([
                Context._single_state_as_vector_data(state),
                action.action_vector
            ])
        # a single context vector entry consists of a state and action both as vectors and concatenated
        padding = numpy.zeros(STATE_SHAPE[0] + NUM_ACTIONS) * missing_context
        return ret + padding

    @staticmethod
    def _single_state_as_vector_data(state):
        return [state.intent_vector, state.sentiment, state.user_profile_vector]

    @staticmethod
    def get_contexts_from_turns(turns: List[Turn], context_length: int = CONTEXT_LENGTH) -> List["Context"]:
        """
        This methods parameters are ordering sensitive! Read below for more information
        Creates Context objects from a list of Turns. The list of Turns needs to be in correct order, i.e.
        the newest (latest) Turn needs to be the last in the list.
        :param turns: the turns to process into contexts, ordering matters, see above!
        :param context_length: number of steps into the past, see parameter in Context.__init__
        :return: a list of Context objects
        """
        contexts = []
        num_turns = len(turns)
        turns = reversed(turns)
        for i, turn in enumerate(turns):
            remaining_turns = min(num_turns - i, context_length)
            turns_slice = turns[i:i + remaining_turns]
            states = [turn.user for turn in turns_slice]
            actions = [turn.bot.action_vector for turn in turns_slice]
            contexts.append(Context(states, actions, context_length))
        return contexts
