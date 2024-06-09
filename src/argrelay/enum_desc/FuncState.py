from enum import Enum, auto


class FuncState(Enum):
    """
    State of the func (its readiness).
    """

    unplugged = auto()
    """
    Used for func that are not plugged anywhere in the tree (but they are published).

    See `AbstractDelegator.get_supported_func_envelopes`.
    """

    ignorable = auto()
    """
    Not `unplugged`, but still not very useful.
    """

    demo = auto()
    """
    Not meant to work - for `argrelay` demo only.
    """

    alpha = auto()
    """
    In alpha testing.
    """

    beta = auto()
    """
    In beta testing.
    """

    gamma = auto()
    """
    GA (general availability)
    """

    def __str__(self):
        return self.name
