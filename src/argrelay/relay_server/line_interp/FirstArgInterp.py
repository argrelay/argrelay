from argrelay.api_ext.relay_server.AbstractInterp import AbstractInterp
from argrelay.relay_server.call_context import CommandContext


class FirstArgInterp(AbstractInterp):
    """
    Dispatch command line interpretation to the next interpreter based on the value in the 1st token (`PosArg`).
    """

    command_name: str

    def __init__(self, command_ctx: CommandContext, config_dict: dict):
        super().__init__(command_ctx, config_dict)

    def consume_pos_args(self) -> None:
        command_name_arg_ipos = 0
        assert self.is_pos_arg(command_name_arg_ipos)
        if command_name_arg_ipos in self.command_ctx.unconsumed_tokens:
            self.command_name = self.command_ctx.parsed_ctx.all_tokens[command_name_arg_ipos]
            del self.command_ctx.unconsumed_tokens[command_name_arg_ipos]
            self.command_ctx.consumed_tokens.append(command_name_arg_ipos)
        else:
            raise LookupError()

    def next_interp(self) -> "AbstractInterp":
        next_interp = self.config_dict["first_arg_vals_to_next_interp_factory_ids"][self.command_name]
        return self.command_ctx.create_next_interp(next_interp)
