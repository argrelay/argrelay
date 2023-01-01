from argrelay.interp_plugin.AbstractInterp import AbstractInterp
from argrelay.runtime_context.InterpContext import InterpContext


class AbstractInterpFactory:
    config_dict: dict

    def __init__(self, config_dict: dict):
        self.config_dict = config_dict

    def create_interp(self, interp_ctx: InterpContext) -> AbstractInterp:
        pass
