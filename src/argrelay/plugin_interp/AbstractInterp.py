from argrelay.enum_desc.InterpStep import InterpStep
from argrelay.enum_desc.TokenType import get_token_type, TokenType

from argrelay.runtime_context.InterpContext import InterpContext

# `AbstractInterp` is NOT a plugin `AbstractInterpFactory` is:
class AbstractInterp:
    """
    Interpreter processes command line sharing current state via :class:`InterpContext`.

    New instance of interpreter is created by (a plugin implementing) `AbstractInterpFactory` for each request.
    """

    instance_counter: int = 0
    """
    Instance counter per interp class.
    """

    def __init__(
        self,
        interp_factory_id: str,
        interp_tree_node_config_dict: dict,
        interp_ctx: InterpContext,
    ):
        self.interp_factory_id: str = interp_factory_id

        self.__class__.instance_counter += 1
        self.instance_number: int = self.instance_counter

        self.interp_tree_node_config_dict: dict = interp_tree_node_config_dict
        """
        The configs for individual `AbstractInterp` are called `interp_tree_node_config_dict` and cloned/populated by
        `load_func_envelopes` based on their position in FS_01_89_09_24 interp tree.
        """

        self.interp_ctx: InterpContext = interp_ctx
        self.base_container_ipos: int = interp_ctx.curr_container_ipos

    def __str__(self) -> str:
        return f"fid: {self.interp_factory_id} path: {self.interp_ctx.interp_tree_abs_path} instance: {self.instance_number}"

    def consume_key_args(self) -> None:
        pass

    def consume_pos_args(self) -> None:
        pass

    def try_iterate(self) -> InterpStep:
        pass

    def has_fill_control(
        self,
    ) -> bool:
        """
        FS_72_53_55_13: See `AbstractDelegator.has_fill_control` for more information.
        """
        return False

    def delegate_fill_control(
        self,
    ) -> bool:
        """
        FS_72_53_55_13: See `AbstractDelegator.run_fill_control` for more information.
        """
        return False

    def propose_arg_completion(self) -> None:
        pass

    def next_interp(self) -> "AbstractInterp":
        """
        Return next interp factory id (or None).
        """
        return None

    def is_pos_arg(
        self,
        token_ipos: int,
    ) -> bool:
        return get_token_type(
            self.interp_ctx.parsed_ctx.all_tokens,
            token_ipos,
        ) is TokenType.PosArg
