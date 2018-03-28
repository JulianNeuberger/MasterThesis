class NoIntentError(Exception):
    def __init__(self, sentence):
        self.sentence = sentence

    def __str__(self) -> str:
        return 'Sentence "{}" has no intent'.format(self.sentence)


class IntentError(Exception):
    def __init__(self, intent, sentence):
        super().__init__()
        self.intent = intent
        self.sentence = sentence


class NoStateIntentError(IntentError):
    def __str__(self) -> str:
        return 'Sentence {} is a state, but has an intent, that is not usable in a state: {}'.format(
            self.sentence,
            self.intent
        )


class NoActionIntentError(IntentError):
    def __str__(self) -> str:
        return 'Sentence {} is an action, but has an intent, that is not usable in an action: {}'.format(
            self.sentence,
            self.intent.template.name
        )


class TurnNotUsable(Exception):
    def __init__(self, root: Exception = None):
        self.root = root
