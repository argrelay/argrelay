from argrelay.relay_server.call_context import CommandContext
from argrelay.relay_server.meta_data import TokenType
from argrelay.relay_server.meta_data.TokenType import get_token_type


class AbstractInterp:
    """
    Interpret command line sharing current state via :class:`CommandContext`.
    """

    command_ctx: CommandContext

    config_dict: dict

    def __init__(self, command_ctx: CommandContext, config_dict: dict):
        self.command_ctx = command_ctx
        self.config_dict = config_dict

    def consume_key_args(self) -> None:
        pass

    def consume_pos_args(self) -> None:
        pass

    def propose_arg_completion(self) -> None:
        pass

    def next_interp(self) -> "AbstractInterp":
        pass

    def is_pos_arg(self, token_ipos: int) -> bool:
        return get_token_type(self.command_ctx.parsed_ctx.all_tokens, token_ipos) == TokenType.PosArg
