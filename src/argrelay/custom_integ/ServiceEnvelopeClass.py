from enum import Enum, auto


class ServiceEnvelopeClass(Enum):
    class_cluster = auto()
    class_host = auto()
    class_service = auto()
    class_access_type = auto()

    def __str__(self):
        return self.name
