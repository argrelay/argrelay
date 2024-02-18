from enum import Enum, auto


class ReservedEnvelopeClass(Enum):
    ClassUnknown = auto()
    ClassFunction = auto()
    ClassHelp = auto()

    def __str__(self):
        return self.name
