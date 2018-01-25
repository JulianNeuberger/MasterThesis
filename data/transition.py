import logging
from typing import List

from data.exceptions import NoIntentError, IntentError, NoStateIntentError, TurnNotUsable, NoActionIntentError
from data.turn import Turn

logger = logging.getLogger("data")


class Transition:
    def __init__(self, start_turn: Turn, next_turn: Turn):
        """
        creates a transition from one turn to the other
        :param start_turn: the first turn
        :param next_turn: the second turn
        """
        logger.debug('Trying to create Transition from turns "{}", "{}"'.format(
            start_turn, next_turn
        ))
        try:
            self.state = start_turn.user
            self.next_state = next_turn.user
            self.action = start_turn.bot
            self.reward = start_turn.bot.reward
            self.terminal = next_turn.bot.terminal
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

    @staticmethod
    def get_transitions_from_turns(turns: List[Turn]):
        """
        extracts Transitions from Turns, used in training of Q-Learning based reinforcement learning techniques
        :param turns: a List of Turns to turn into Transitions
        :return: a List of Transitions extracted from the given Turns
        """
        num_turns = len(turns)
        transitions = []
        for i, turn in enumerate(turns):
            try:
                if i < (num_turns - 1):
                    # is there a next turn after this one?
                    next_turn = turns[i + 1]
                    if next_turn.dialogue == turn.dialogue:
                        # same conversation?
                        # we need to check this, since this are all turns, regardless of dialogue
                        transitions.append(Transition(turn, next_turn))
            except TurnNotUsable:
                logger.warning(
                    'Turn "{}" -> "{}" can not be used, see warnings above, skipping it.'.format(turn[0], turn[1]))
        return transitions
