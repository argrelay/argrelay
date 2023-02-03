from argrelay.enum_desc.InterpStep import InterpStep
from argrelay.enum_desc.TokenType import get_token_type, TokenType

from argrelay.runtime_context.InterpContext import InterpContext


class AbstractInterp:
    """
    Interpret command line sharing current state via :class:`InterpContext`.
    """

    interp_ctx: InterpContext

    config_dict: dict

    def __init__(self, interp_ctx: InterpContext, config_dict: dict):
        self.interp_ctx = interp_ctx
        self.config_dict = config_dict

    def consume_key_args(self) -> None:
        pass

    def consume_pos_args(self) -> None:
        pass

    def try_iterate(self) -> InterpStep:
        pass

    def propose_arg_completion(self) -> None:
        pass

    def next_interp(self) -> "AbstractInterp":
        pass

    def is_pos_arg(self, token_ipos: int) -> bool:
        return get_token_type(self.interp_ctx.parsed_ctx.all_tokens, token_ipos) == TokenType.PosArg
