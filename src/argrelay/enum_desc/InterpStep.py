from enum import Enum, auto


class InterpStep(Enum):
    StopAll = auto()
    """
    No way to continue interpretation - no enough info.
    """

    NextEnvelope = auto()
    """
    Current search yields single `data_envelope`, move to search the next envelope.
    """

    NextInterp = auto()
    """
    All `data_envelope`-s for current interpreter have been found, switch to the next interpreter.
    """
