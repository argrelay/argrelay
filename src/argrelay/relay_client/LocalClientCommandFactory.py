from argrelay.client_command_local.AbstractLocalClientCommand import AbstractLocalClientCommand
from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.misc_helper.ElapsedTime import ElapsedTime
from argrelay.relay_client.AbstractClientCommandFactory import AbstractClientCommandFactory
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.schema_config_core_server.ServerConfigSchema import server_config_desc
from argrelay.server_spec.CallContext import CallContext


class LocalClientCommandFactory(AbstractClientCommandFactory):

    def __init__(self):
        self._start_local_server()

    def _start_local_server(self):
        self.server_config: ServerConfig = server_config_desc.from_default_file()
        ElapsedTime.measure("after_server_config_load")
        self.local_server: LocalServer = LocalServer(self.server_config)
        self.local_server.start_local_server()
        ElapsedTime.measure("after_local_server_start")

    def create_command_by_server_path(
        self,
        call_ctx: CallContext,
    ) -> AbstractLocalClientCommand:
        if call_ctx.server_action == ServerAction.DescribeLineArgs:
            from argrelay.client_command_local.DescribeLineArgsLocalClientCommand import (
                DescribeLineArgsLocalClientCommand
            )
            return DescribeLineArgsLocalClientCommand(
                call_ctx,
                self.server_config,
                self.local_server,
            )
        if call_ctx.server_action == ServerAction.ProposeArgValues:
            from argrelay.client_command_local.ProposeArgValuesLocalClientCommand import (
                ProposeArgValuesLocalClientCommand
            )
            return ProposeArgValuesLocalClientCommand(
                call_ctx,
                self.server_config,
                self.local_server,
            )
        if call_ctx.server_action == ServerAction.RelayLineArgs:
            from argrelay.client_command_local.RelayLineArgsLocalClientCommand import (
                RelayLineArgsLocalClientCommand
            )
            return RelayLineArgsLocalClientCommand(
                call_ctx,
                self.server_config,
                self.local_server,
            )
        raise RuntimeError
