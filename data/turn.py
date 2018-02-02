import logging
from typing import List, Union, Tuple

from data.action import Action
from data.exceptions import NoIntentError, IntentError, TurnNotUsable
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
        :raises TurnNotUsable: if any of the two sentences is not processable
        """
        try:
            self.user = State(first)
            self.bot = Action(second)
        except NoIntentError or IntentError as e:
            raise TurnNotUsable(e)
        assert first.said_in == second.said_in
        self.dialogue = first.said_in

    @staticmethod
    def sentences_to_turns(sentences: List[Sentence]) -> List["Turn"]:
        """
        Makes Turn objects from Sentences. Is ordering sensitive, expects you to provide sentences ordered
        from oldest to latest
        :param sentences: a List of Sentences, ordered from oldest to newest
        :return: a List of Turns created from these Sentences with an optional Sentence, representing the last
        """
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
                try:
                    turns.append(Turn(first, second))
                except:
                    logger.warning("Cannot use turn '{}'->'{}'".format(first, second))
        return turns
