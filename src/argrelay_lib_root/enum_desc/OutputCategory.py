from enum import (
    auto,
    Enum,
)


class OutputCategory(Enum):
    is_failure = auto()
    is_warning = auto()
    is_offline = auto()
    is_success = auto()
