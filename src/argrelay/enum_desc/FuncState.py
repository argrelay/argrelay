from enum import Enum, auto


class FuncState(Enum):
    """
    State of the func (its readiness).
    """

    fs_unplugged = auto()
    """
    Used for func that are not plugged anywhere in the tree (but they are published).

    See `DelegatorAbstract.get_supported_func_envelopes`.
    """

    fs_ignorable = auto()
    """
    Not `fs_unplugged`, but still not very useful.
    """

    fs_demo = auto()
    """
    Not meant to work - for `argrelay` demo only.
    """

    fs_alpha = auto()
    """
    In "alpha" testing.
    """

    fs_beta = auto()
    """
    In "beta" testing.
    """

    fs_gamma = auto()
    """
    In GA (general availability).
    """

    def __str__(self):
        return self.name
