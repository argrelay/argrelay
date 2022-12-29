from enum import Enum, auto


class ReservedObjectClass(Enum):
    ClassFunction = auto()

    def __str__(self):
        return self.name
