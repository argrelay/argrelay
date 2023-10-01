from __future__ import annotations

from enum import Enum, auto

from argrelay.enum_desc.CompType import CompType


class CallConv(Enum):
    """
    `CallConv` defines calling convention between Shell and `argrelay` client.

    `CallConv` is closely related to `RunMode`.

    It tells how data is passed from Shell to argrelay client (similar concept to C/C++ calling conventions):
    *   `CallConv.CliArgsConv` is used for `RunMode.Invocation` to pass data via command line args.
    *   `CallConv.EnvVarsConv` is used for `RunMode.Completion` to pass data via env vars.
    """

    CliArgsConv = auto()
    EnvVarsConv = auto()

    def __str__(self):
        return self.name

    @classmethod
    def from_comp_type(
        cls,
        comp_type: CompType,
    ) -> CallConv:
        """
        Derive `CallConv` on client side from `CompType`.
        """

        if comp_type is CompType.InvokeAction:
            return CallConv.CliArgsConv
        else:
            return CallConv.EnvVarsConv
