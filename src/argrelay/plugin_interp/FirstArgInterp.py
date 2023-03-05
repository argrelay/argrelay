from argrelay.enum_desc.InterpStep import InterpStep
from argrelay.plugin_interp.AbstractInterp import AbstractInterp
from argrelay.plugin_interp.FirstArgInterpFactoryConfigSchema import first_arg_vals_to_next_interp_factory_ids_
from argrelay.runtime_context.InterpContext import InterpContext


class FirstArgInterp(AbstractInterp):
    """
    Dispatch command line interpretation to the next interpreter
    based on the value in the very 1st token (`PosArg`) (with 0 ipos).

    Implements FS_42_76_93_51.
    """

    command_name: str

    def __init__(
        self,
        interp_factory_id: str,
        config_dict: dict,
        interp_ctx: InterpContext,
    ):
        super().__init__(
            interp_factory_id,
            config_dict,
            interp_ctx,
        )

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
        interp_factory_id = self.config_dict[first_arg_vals_to_next_interp_factory_ids_][self.command_name]
        return self.interp_ctx.create_next_interp(interp_factory_id)
