from argrelay.api_ext.relay_server.AbstractInterp import AbstractInterp
from argrelay.relay_server.call_context import CommandContext


class AbstractInterpFactory:
    config_dict: dict

    def __init__(self, config_dict: dict):
        self.config_dict = config_dict

    def create_interp(self, command_context: CommandContext) -> AbstractInterp:
        pass
