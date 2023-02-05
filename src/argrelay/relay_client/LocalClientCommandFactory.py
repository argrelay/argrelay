from argrelay.client_command_local.AbstractLocalClientCommand import AbstractLocalClientCommand
from argrelay.misc_helper.ElapsedTime import ElapsedTime
from argrelay.relay_client.AbstractClientCommandFactory import AbstractClientCommandFactory
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.schema_config_core_server.ServerConfigSchema import server_config_desc
from argrelay.server_spec.const_int import (
    DESCRIBE_LINE_ARGS_PATH,
    RELAY_LINE_ARGS_PATH,
    PROPOSE_ARG_VALUES_PATH,
)


class LocalClientCommandFactory(AbstractClientCommandFactory):
    server_config: ServerConfig
    local_server: LocalServer

    def __init__(self):
        self._start_local_server()

    def _start_local_server(self):
        self.server_config = server_config_desc.from_default_file()
        ElapsedTime.measure("after_server_config_load")
        self.local_server = LocalServer(self.server_config)
        self.local_server.start_local_server()
        ElapsedTime.measure("after_local_server_start")

    def create_command_by_server_path(self, server_path: str) -> AbstractLocalClientCommand:
        if server_path == DESCRIBE_LINE_ARGS_PATH:
            from argrelay.client_command_local.DescribeLineArgsLocalClientCommand import (
                DescribeLineArgsLocalClientCommand
            )
            return DescribeLineArgsLocalClientCommand(
                self.server_config,
                self.local_server,
            )
        if server_path == PROPOSE_ARG_VALUES_PATH:
            from argrelay.client_command_local.ProposeArgValuesLocalClientCommand import (
                ProposeArgValuesLocalClientCommand
            )
            return ProposeArgValuesLocalClientCommand(
                self.server_config,
                self.local_server,
            )
        if server_path == RELAY_LINE_ARGS_PATH:
            from argrelay.client_command_local.RelayLineArgsLocalClientCommand import (
                RelayLineArgsLocalClientCommand
            )
            return RelayLineArgsLocalClientCommand(
                self.server_config,
                self.local_server,
            )
        raise RuntimeError
