from argrelay.enum_desc.InterpStep import InterpStep
from argrelay.plugin_interp.AbstractInterp import AbstractInterp


class NoopInterp(AbstractInterp):
    """
    Interpreter which does nothing

    It stops processing of the command line on itself (as `next_interp` returns `None` by default)
    """

    def try_iterate(self) -> InterpStep:
        return InterpStep.NextInterp
