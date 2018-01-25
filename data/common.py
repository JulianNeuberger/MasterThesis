from typing import List, Optional, Tuple

from turns.models import Sentence


def produce_turns_from_sentence_list(sentences: List[Sentence], user_name: str = None, bot_name: str = None) \
        -> List[Tuple[Sentence, Optional[Sentence]]]:
    check_names = user_name is not None and bot_name is not None
    pairs = zip(sentences[::2], sentences[1::2])
    turns = []
    for first, second in pairs:
        if check_names:
            unknown_name = 'Sentence {} is said by third party {}'
            assert first.said_by == user_name or first.said_by == bot_name, unknown_name.format(first, first.said_by)
            assert second.said_by == user_name or second.said_by == bot_name, unknown_name.format(second, second.said_by)

        if first.said_by == second.said_by:
            if check_names:
                # one participant said nothing
                assert first.said_by == user_name, 'A bot is not allowed to double post messages!'
            turns.append((first, None))
            turns.append((second, None))
        else:
            if check_names:
                assert first.said_by == user_name, 'Bot can only react to user input'
            turns.append((first, second))
    return turns


def pad_context(context: List, pad_to_length: int):
    if len(context) < pad_to_length:
        missing = pad_to_length - len(context)
        padding = [None] * missing
        context = context + padding
    return context
