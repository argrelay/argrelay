from enum import Enum, auto


class ServiceEnvelopeClass(Enum):
    ClassService = auto()
    ClassHost = auto()

    def __str__(self):
        return self.name
