from argrelay.misc_helper.AbstractPlugin import AbstractPlugin
from argrelay.plugin_interp.AbstractInterp import AbstractInterp
from argrelay.runtime_context.InterpContext import InterpContext


class AbstractInterpFactory(AbstractPlugin):

    def create_interp(
        self,
        interp_ctx: InterpContext,
    ) -> AbstractInterp:
        pass
