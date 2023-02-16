from enum import Enum, auto


class ServiceEnvelopeClass(Enum):
    ClassCluster = auto()
    ClassHost = auto()
    ClassService = auto()

    def __str__(self):
        return self.name
