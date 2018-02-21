import logging
from copy import copy
from typing import List, Tuple

import numpy

from bot.config import NUM_ACTIONS, STATE_SHAPE, CONTEXT_LENGTH
from data.action import Action
from data.state import State

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
        assert new_val >= 0, 'context length can not be less than 0'
        if self._actions is not None:
            assert new_val >= len(self._actions), 'New context length is shorter than the number of available actions!'
        if self._states is not None:
            assert new_val >= len(self._states), 'New context length is shorter than the number of available states!'
        self._context_length = new_val

    def as_matrix(self) -> numpy.array:
        """
        Gets this context in matrix representation.
        Concatenates state and action (in vector form) for each context step

        :return: matrix representation for this context, shape of (CONTEXT_LENGTH, STATE_SHAPE[0]+NUM_ACTIONS)
        """
        # number of missing actions/states
        missing_context = self.context_length - len(self.actions)
        # if missing_context != 0:
        # logger.debug("Missing {} turns for context".format(
        #     missing_context
        # ))
        ret = []
        if self.states is not None and self.actions is not None:
            for state, action in zip(self.states, self.actions):
                entry = numpy.concatenate((state.as_vector(), action.as_vector()))
                ret.append(entry)
        # a single context vector entry consists of a state and action both as vectors and concatenated
        padding = numpy.zeros((missing_context, STATE_SHAPE[0] + NUM_ACTIONS))
        ret = numpy.array(ret)
        # logger.debug("Shape of known contexts is {}, while shape of padding is {}".format(ret.shape, padding.shape))
        if len(ret) is not 0:
            ret = numpy.concatenate((ret, padding))
        else:
            ret = padding
        return ret

    def push(self, state: State, action: Action):
        """
        Updates this context with a given state and action,
        equivalent to the concept of "moving one step into the future"

        Does not mutate the original object

        :param state: the latest state (s_t-1)
        :param action: the action that is taken in this state (a_t-1)
        :return: the new context object, does not return the old one as mutation
        """
        context = copy(self)

        if len(context.states) == context.context_length:
            context.states.pop()
        context.states.insert(0, state)

        if len(context.actions) == context.context_length:
            context.actions.pop()
        context.actions.insert(0, action)

        return context

    @staticmethod
    def get_single_context(turns, context_length: int = CONTEXT_LENGTH):
        """
        Creates a context object from turns, useful for training
        :param turns: the Turns that make up the context, e.g. the turns prior to the current Sentence/State
        :param context_length: number of steps into the past
        :return: a Context object see __init__
        """
        assert len(turns) <= context_length
        states = [turn.user for turn in turns]
        actions = [turn.bot for turn in turns]
        return Context(states, actions, context_length)

    def to_data_tuple(self) -> Tuple[State, "Context", Action]:
        """
        returns context as tuple of state, context with one less "past" step and action
        :return: a Tuple of State, Context and Action used in training
        """
        context = copy(self)

        logger.debug('Converting context of length {} with {} states and actions to data tuple'.format(
            context.context_length,
            len(context.actions)
        ))

        assert len(context.actions) > 0, 'Cannot convert empty context to data tuple'
        before_num = len(context.actions)
        action = context.actions.pop(0)
        after_num = len(context.actions)
        logger.debug('Truncating context actions from {} to {}'.format(
            before_num,
            after_num
        ))

        assert len(context.states) > 0, 'Cannot convert empty context to data tuple'
        state = context.states.pop(0)

        context.context_length = max(context.context_length - 1, 0)

        return state, context, action

    def __str__(self) -> str:
        formatted_states = ['{}'.format(state) for state in self.states]
        formatted_actions = ['{}'.format(action) for action in self.actions]
        return '<Context states: "{}", actions "{}">'.format(formatted_states, formatted_actions)

    def __format__(self, format_spec: str) -> str:
        return super().__format__(format_spec)
