from __future__ import annotations

from enum import Enum, auto

from argrelay.enum_desc.CompType import CompType


class RunMode(Enum):
    """
    Note: `RunMode` became completely implied by `ServerAction` and it is not used for logic anymore.

    See also `CallConv`.

    `RunMode` originates on the client side because of different user actions:
    *   `CompletionMode`: user hits `Tab` trying to complete command line arg.
    *   `InvocationMode`: user hits `Enter` trying to execute the command line.
    Request to `argrelay` server indicates the two different modes:
    *   `CompletionMode` - when shell asks `argrelay` server for suggestions to complete one command line arg.
    *   `InvocationMode` - when already executed command uses `argrelay` to determine values for all args.
    In other words:
    *   `CompletionMode` = (proposing options) collects all possible value options for the single arg under cursor.
    *   `InvocationMode` = (exercising options) selects only one value for specific arg, but does it for every arg.
    Also:
    *   `CompletionMode` excludes tangent token ("touched" by the cursor) as input to provide completion for it.
    *   `InvocationMode` includes tangent token as input arg to execute selected function.
    """

    CompletionMode = auto()
    InvocationMode = auto()

    def __str__(self):
        return self.name

    @classmethod
    def from_comp_type(
        cls,
        comp_type: CompType,
    ) -> RunMode:
        """
        Derive `RunMode` on client side from `CompType`.
        """

        if comp_type is CompType.InvokeAction:
            return RunMode.InvocationMode
        else:
            return RunMode.CompletionMode
