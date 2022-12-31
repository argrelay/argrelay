from argrelay.interp_plugin.AbstractInterp import AbstractInterp
from argrelay.runtime_context.CommandContext import CommandContext


class AbstractInterpFactory:
    config_dict: dict

    def __init__(self, config_dict: dict):
        self.config_dict = config_dict

    def create_interp(self, command_context: CommandContext) -> AbstractInterp:
        pass
