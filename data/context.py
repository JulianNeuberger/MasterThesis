import logging
from typing import List

import numpy

from bot.config import CONTEXT_LENGTH, NUM_ACTIONS, STATE_SHAPE
from data.action import Action
from data.state import State
from data.turn import Turn

logger = logging.getLogger('data')


class Context:
    """
    An object representing a stack of turns of format State->Action.
    Index 0 is the current turn, all following are "one step into the past"
    """

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
        self._context_length = context_length

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
        missing_context = self.context_length - len(self.actions)
        logger.debug("Missing {}-{}={} turns for context".format(
            self.context_length,
            len(self.actions),
            missing_context
        ))
        ret = []
        if self.states is not None and self.actions is not None:
            for state, action in zip(self.states, self.actions):
                entry = numpy.concatenate((state.as_vector(), action.as_vector()))
                ret.append(entry)
        # a single context vector entry consists of a state and action both as vectors and concatenated
        padding = numpy.zeros((missing_context, STATE_SHAPE[0] + NUM_ACTIONS))
        ret = numpy.array(ret)
        logger.debug("Shape of known contexts is {}, while shape of padding is {}".format(ret.shape, padding.shape))
        if len(ret is not 0):
            ret = numpy.concatenate((ret, padding))
        else:
            ret = padding
        return ret

    @staticmethod
    def get_contexts_from_turns(turns: List[Turn], context_length: int = CONTEXT_LENGTH) -> numpy.ndarray:
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
        turns = turns[::-1]
        for i, turn in enumerate(turns):
            remaining_turns = min(num_turns - i, context_length)
            turns_slice = turns[i:i + remaining_turns]
            contexts.append(Context.get_single_context(turns_slice, context_length))
        return numpy.array(contexts)

    @staticmethod
    def get_single_context(turns, context_length: int = CONTEXT_LENGTH):
        assert len(turns) <= CONTEXT_LENGTH
        states = [turn.user for turn in turns]
        actions = [turn.bot for turn in turns]
        return Context(states, actions, context_length)
