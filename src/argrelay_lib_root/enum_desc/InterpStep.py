from enum import (
    auto,
    Enum,
)


class InterpStep(Enum):
    """
    Step decision in interpretation loop - see `InterpContext.interpret_command`.
    """

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
