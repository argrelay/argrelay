from enum import Enum, auto


class ReservedEnvelopeClass(Enum):
    ClassFunction = auto()
    ClassHelp = auto()

    def __str__(self):
        return self.name
