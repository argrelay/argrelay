from __future__ import annotations

from argrelay.plugin_interp.FuncArgsInterp import FuncArgsInterp
from argrelay.runtime_context.InterpContext import InterpContext


class FuncTreeInterp(FuncArgsInterp):
    """
    Implements FS_26_43_73_72 func tree.
    """

    def __init__(
        self,
        interp_factory_id: str,
        config_dict: dict,
        interp_ctx: InterpContext,
        func_paths: dict[str, list[list[str]]],
    ):
        super().__init__(
            interp_factory_id,
            config_dict,
            interp_ctx,
            func_paths,
        )
