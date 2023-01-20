from enum import Enum, auto


class ServiceEnvelopeClass(Enum):
    ClassCluster = auto()
    ClassService = auto()
    ClassHost = auto()

    def __str__(self):
        return self.name
