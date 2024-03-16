from enum import Enum, auto


class ServiceEnvelopeClass(Enum):
    ClassCluster = auto()
    ClassHost = auto()
    ClassService = auto()
    ClassAccessType = auto()

    def __str__(self):
        return self.name
