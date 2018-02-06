import logging
from typing import List, Iterator

from django.contrib.auth.models import User

from data.action import Action
from data.exceptions import NoIntentError, IntentError, TurnNotUsable, NoActionIntentError, NoStateIntentError
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
            self._first = first
            self._second = second
        except NoIntentError or IntentError as e:
            raise TurnNotUsable(e)
        assert first.said_in == second.said_in
        self.dialogue = first.said_in

    @staticmethod
    def sentences_to_turns(sentences: List[Sentence], bot_user:User) -> List["Turn"]:
        """
        Makes Turn objects from Sentences. Is ordering sensitive, expects you to provide sentences ordered
        from oldest to latest
        :param bot_user: The user object, corresponding to the bot user, needed for identifying bot actions
        :param sentences: a List of Sentences, ordered from oldest to newest
        :return: a List of Turns created from these Sentences with an optional Sentence, representing the last
        """
        turns = []
        sentences_iter = iter(sentences)
        for first in sentences_iter:
            if first.said_by == bot_user.username:
                continue
            try:
                second = Turn._find_second(sentences_iter, first)
            except StopIteration:
                # no more sentences
                break
            try:
                turn = Turn(first, second)
                turns.append(turn)
                logger.info("Successfully parsed {}".format(turn))
            except NoIntentError or NoActionIntentError or NoStateIntentError as e:
                logger.warning("Cannot use turn '{}'->'{}' because of '{}'".format(first, second, e))
        return turns

    @staticmethod
    def _find_second(iterator: Iterator, first):
        """
        Skips double posts and raises StopIteration exception, when no more sentences
        :param iterator: a iterator to skim for the second sentence
        :param first: the first sentence
        :return: a Sentence, that completes the Turn, e.g. said by a person other than the one in "first"
        """
        second = None
        while second is None or second.said_by == first.said_by:
            second = next(iterator)
        return second

    def __str__(self) -> str:
        return 'Turn({}->{})'.format(self._first, self._second)
