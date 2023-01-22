from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.RunMode import RunMode

from argrelay.relay_demo.ServiceArgType import ServiceArgType
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_data import StaticData
from argrelay.runtime_data.AssignedValue import AssignedValue


# TODO: class is not used anymore - the same functionality has to be addressed somehow generically (or at least, should be reimplemented, current approach here got in the way of more important feature and removed temporarily)
class CodeMaturityProcessor:

    def __init__(self, static_data: StaticData, arg_key: str):
        super().__init__(static_data, arg_key, ServiceArgType.CodeMaturity.name)

    def try_implicit_arg(self, ctx: InterpContext) -> bool:
        if ctx.parsed_ctx.run_mode == RunMode.InvocationMode:
            # TODO: generalize: this can be configured: what assigned (ServiceArgType, arg_value) gives other list of (ServiceArgType, arg_value):
            #                   This situation should be a generic one - providing defaults based currently assigned values.
            #                   Note that defaults and implicit values are different:
            #                   - defaults de-prioritize proposing values for the type if it got default value under current context.
            #                   - implicit values make type assigned (with that value) and it should not be asked for value anymore.
            if self.arg_type in ctx.curr_assigned_types_to_values:
                # Assign AccessType if it was not specified (explicitly):
                if ServiceArgType.AccessType.name not in ctx.curr_assigned_types_to_values:
                    if ctx.curr_assigned_types_to_values[self.arg_type].arg_value == "prod":
                        ctx.curr_assigned_types_to_values[ServiceArgType.AccessType.name] = AssignedValue(
                            "ro",
                            ArgSource.ImplicitValue,
                        )
                        return True
                    else:
                        ctx.curr_assigned_types_to_values[ServiceArgType.AccessType.name] = AssignedValue(
                            "rw",
                            ArgSource.ImplicitValue,
                        )
                        return True
        return False
