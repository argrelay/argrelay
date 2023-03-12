from enum import Enum, auto


class ReservedArgType(Enum):
    EnvelopeClass = auto()
    ArgType = auto()
    ArgValue = auto()
    HelpHint = auto()
