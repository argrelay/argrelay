from enum import Enum, auto


class GlobalArgType(Enum):
    FunctionCategory = auto()
    """
    A way to separate functions in different "buckets".

    For example:
    *   "internal" provided by `argrelay` for various built-in and support functions
    *   "external" provided by plugins for domain-specific
    """

    ActionType = auto()
    """
    Specifies what function does. For example: "goto", "list", ...
    """

    ObjectSelector = auto()
    """
    Specifies what kind of objects a function works with. For example: "host", "service", ...
    """
