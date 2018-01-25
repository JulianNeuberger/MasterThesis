class NoIntentError(Exception):
    def __init__(self, sentence):
        self.sentence = sentence


class IntentError(Exception):
    def __init__(self, intent):
        super().__init__()
        self.intent = intent


class NoStateIntentError(IntentError):
    pass


class NoActionIntentError(IntentError):
    pass


class TurnNotUsable(Exception):
    pass
