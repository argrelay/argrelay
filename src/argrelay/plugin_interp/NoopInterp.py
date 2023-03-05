from argrelay.enum_desc.InterpStep import InterpStep
from argrelay.plugin_interp.AbstractInterp import AbstractInterp
from argrelay.runtime_context.InterpContext import InterpContext


class NoopInterp(AbstractInterp):
    """
    Interpreter which does nothing

    Actually, it:
    *   stops processing of the command line on itself (as `next_interp` returns `None` by default)
    *   sets `arbitrary_comment` based on config
    """

    arbitrary_comment: str

    def __init__(
        self,
        interp_factory_id,
        config_dict: dict,
        interp_ctx: InterpContext,
    ):
        super().__init__(
            interp_factory_id,
            config_dict,
            interp_ctx,
        )
        self.arbitrary_comment = config_dict["arbitrary_comment"]

    def try_iterate(self) -> InterpStep:
        return InterpStep.NextInterp
