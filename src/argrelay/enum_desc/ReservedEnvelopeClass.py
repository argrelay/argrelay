from enum import Enum, auto


class ReservedEnvelopeClass(Enum):
    """
    Names of the `data_envelope` classes reserved by `argrelay`.
    """

    ClassUnknown = auto()

    ClassFunction = auto()

    ClassHelp = auto()

    def __str__(self):
        return self.name
