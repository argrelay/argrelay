from argrelay.api_ext.relay_server import StaticData
from argrelay.api_int.meta_data import ArgValue, ArgSource
from argrelay.api_int.meta_data.RunMode import RunMode
from argrelay.relay_demo.ServiceArgType import ServiceArgType
from argrelay.relay_server.arg_processor.ArgProcessor import ArgProcessor
from argrelay.relay_server.call_context import CommandContext


class CodeMaturityProcessor(ArgProcessor):

    def __init__(self, static_data: StaticData, arg_key: str):
        super().__init__(static_data, arg_key, ServiceArgType.CodeMaturity.name)

    def try_implicit_arg(self, ctx: CommandContext) -> bool:
        if ctx.parsed_ctx.run_mode == RunMode.InvocationMode:
            # TODO: generalize: this can be configured: what assigned (ServiceArgType, arg_value) gives other list of (ServiceArgType, arg_value):
            #                   This situation should be a generic one - providing defaults based currently assigned values.
            #                   Note that defaults and implicit values are different:
            #                   - defaults de-prioritize proposing values for the type if it got default value under current context.
            #                   - implicit values make type assigned (with that value) and it should not be asked for value anymore.
            if self.arg_type in ctx.assigned_types_to_values:
                # Assign AccessType if it was not specified (explicitly):
                if ServiceArgType.AccessType.name not in ctx.assigned_types_to_values:
                    if ctx.assigned_types_to_values[self.arg_type].arg_value == "prod":
                        ctx.assigned_types_to_values[ServiceArgType.AccessType.name] = ArgValue(
                            "ro",
                            ArgSource.ImplicitValue,
                        )
                        return True
                    else:
                        ctx.assigned_types_to_values[ServiceArgType.AccessType.name] = ArgValue(
                            "rw",
                            ArgSource.ImplicitValue,
                        )
                        return True
        return False
