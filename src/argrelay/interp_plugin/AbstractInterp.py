from argrelay.meta_data.TokenType import get_token_type, TokenType
from argrelay.runtime_context.CommandContext import CommandContext


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
