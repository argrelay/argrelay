from enum import Enum, auto


class OutputCategory(Enum):
    is_failure = auto()
    is_warning = auto()
    is_offline = auto()
    is_success = auto()
