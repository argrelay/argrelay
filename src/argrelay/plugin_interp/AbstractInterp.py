from argrelay.enum_desc.InterpStep import InterpStep
from argrelay.enum_desc.TokenType import get_token_type, TokenType

from argrelay.runtime_context.InterpContext import InterpContext


class AbstractInterp:
    """
    Interpret command line sharing current state via :class:`InterpContext`.

    New instance of interpreter is created by (plugin implementing) `AbstractInterpFactory` for each request.
    """

    interp_factory_id: str

    config_dict: dict

    interp_ctx: InterpContext

    def __init__(
        self,
        interp_factory_id: str,
        config_dict: dict,
        interp_ctx: InterpContext,
    ):
        self.interp_factory_id = interp_factory_id
        self.config_dict = config_dict
        self.interp_ctx = interp_ctx
        self.base_envelope_ipos: int = interp_ctx.curr_container_ipos

    def __repr__(self) -> str:
        return f"fid: {self.interp_factory_id}, {super().__repr__()}"

    def consume_key_args(self) -> None:
        pass

    def consume_pos_args(self) -> None:
        pass

    def try_iterate(self) -> InterpStep:
        pass

    def run_fill_control(self) -> None:
        pass

    def propose_arg_completion(self) -> None:
        pass

    def next_interp(self) -> "AbstractInterp":
        """
        Return next interp factory id (or None).
        """
        return None

    def is_pos_arg(self, token_ipos: int) -> bool:
        return get_token_type(self.interp_ctx.parsed_ctx.all_tokens, token_ipos) == TokenType.PosArg
