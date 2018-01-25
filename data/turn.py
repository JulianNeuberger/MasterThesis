import logging
from typing import Iterable, List

from data.action import Action
from data.state import State
from turns.models import Sentence

logger = logging.getLogger("data")


class Turn:
    user = None
    bot = None
    dialogue = None

    def __init__(self, first: Sentence, second: Sentence):
        """
        Creates a turn from two sentences

        :param first: first sentence to use, e.g. the user sentence
        :param second: second sentence, e.g. the bot sentence

        :raises AssertionError: if sentences are in different dialogues
        """
        self.user = State(first)
        self.bot = Action(second)
        assert first.said_in == second.said_in
        self.dialogue = first.said_in

    @staticmethod
    def sentences_to_turns(sentences: Iterable[Sentence]) -> List["Turn"]:
        pairs = zip(sentences[::2], sentences[1::2])
        turns = []
        for first, second in pairs:
            if first.said_by == second.said_by:
                # assume NOP by bot
                # TODO: special action for NOP? this is not supported right now
                # turns.append(Turn(first, None))
                # turns.append(Turn(second, None))
                logger.warning("Double post by user, the bot obviously chose to do nothing or failed doing something, "
                               "NO-OP is not supported by training framework right now. "
                               "Offending sentences are '{}' and '{}'".format(first, second))
            else:
                turns.append(Turn(first, second))
        return turns
