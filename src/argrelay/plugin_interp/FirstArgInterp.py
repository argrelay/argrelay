from argrelay.enum_desc.InterpStep import InterpStep
from argrelay.plugin_interp.AbstractInterp import AbstractInterp
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.schema_config_core_server.FirstArgInterpFactorySchema import first_arg_vals_to_next_interp_factory_ids_


class FirstArgInterp(AbstractInterp):
    """
    Dispatch command line interpretation to the next interpreter based on the value in the 1st token (`PosArg`).
    """

    command_name: str

    def __init__(self, interp_ctx: InterpContext, config_dict: dict):
        super().__init__(interp_ctx, config_dict)

    def consume_pos_args(self) -> None:
        command_name_arg_ipos = 0
        assert self.is_pos_arg(command_name_arg_ipos)
        if command_name_arg_ipos in self.interp_ctx.unconsumed_tokens:
            self.command_name = self.interp_ctx.parsed_ctx.all_tokens[command_name_arg_ipos]
            del self.interp_ctx.unconsumed_tokens[command_name_arg_ipos]
            self.interp_ctx.consumed_tokens.append(command_name_arg_ipos)
        else:
            raise LookupError()

    def try_iterate(self) -> InterpStep:
        return InterpStep.NextInterp

    def next_interp(self) -> "AbstractInterp":
        next_interp = self.config_dict[first_arg_vals_to_next_interp_factory_ids_][self.command_name]
        return self.interp_ctx.create_next_interp(next_interp)
