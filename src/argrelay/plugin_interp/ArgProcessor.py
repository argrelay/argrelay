from __future__ import annotations

from argrelay.meta_data import StaticData
from argrelay.meta_data.ArgSource import ArgSource
from argrelay.meta_data.ArgValue import ArgValue
from argrelay.runtime_context.InterpContext import InterpContext


class ArgProcessor:
    static_data: StaticData
    arg_key: str
    arg_type: str

    def __init__(self, static_data: StaticData, arg_key: str, arg_type: str):
        self.static_data = static_data
        self.arg_key = arg_key
        self.arg_type = arg_type

    def __repr__(self):
        return f"{self.__class__.__name__}({self.arg_type!r})"

    def try_explicit_arg(self, interp_ctx: InterpContext, token: str) -> bool:
        """
        :return: True if any arg was assigned during invocation
        """
        if (
            self.arg_type not in interp_ctx.curr_assigned_types_to_values
            and
            self.arg_type in interp_ctx.curr_remaining_types_to_values
            and
            token in interp_ctx.curr_remaining_types_to_values[self.arg_type]
        ):
            interp_ctx.curr_assigned_types_to_values[self.arg_type] = ArgValue(token, ArgSource.ExplicitArg)
            return True
        else:
            return False

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def try_implicit_arg(self, ctx: InterpContext) -> bool:
        """
        :return: True if any arg was assigned during invocation
        """
        return False
