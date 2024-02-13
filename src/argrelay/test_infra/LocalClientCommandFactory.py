from argrelay.client_command_local.AbstractLocalClientCommand import AbstractLocalClientCommand
from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.misc_helper_common.ElapsedTime import ElapsedTime
from argrelay.relay_client.AbstractClientCommandFactory import AbstractClientCommandFactory
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.schema_config_core_server.ServerConfigSchema import server_config_desc
from argrelay.server_spec.CallContext import CallContext


class LocalClientCommandFactory(AbstractClientCommandFactory):
    local_server: LocalServer = None
    """
    This instance of `LocalServer` allows reusing server for multiple `LocalClient` invocation in tests.
    For example, to avoid re-loading TD_38_03_48_51 large data sets.
    """

    def __init__(self):
        self._start_local_server()

    def _start_local_server(self):
        if not LocalClientCommandFactory.local_server:
            self.server_config: ServerConfig = server_config_desc.obj_from_default_file()
            ElapsedTime.measure("after_server_config_load")
            LocalClientCommandFactory.local_server = LocalServer(self.server_config)
            LocalClientCommandFactory.local_server.start_local_server()
            ElapsedTime.measure("after_local_server_start")
        else:
            self.server_config: ServerConfig = LocalClientCommandFactory.local_server.server_config

    def create_command(
        self,
        call_ctx: CallContext,
    ) -> AbstractLocalClientCommand:
        if call_ctx.server_action is ServerAction.ProposeArgValues:
            from argrelay.client_command_local.ProposeArgValuesLocalClientCommand import (
                ProposeArgValuesLocalClientCommand
            )
            return ProposeArgValuesLocalClientCommand(
                call_ctx,
                self.server_config,
                self.local_server,
            )
        if call_ctx.server_action is ServerAction.DescribeLineArgs:
            from argrelay.client_command_local.DescribeLineArgsLocalClientCommand import (
                DescribeLineArgsLocalClientCommand
            )
            return DescribeLineArgsLocalClientCommand(
                call_ctx,
                self.server_config,
                self.local_server,
            )
        if call_ctx.server_action is ServerAction.RelayLineArgs:
            from argrelay.client_command_local.RelayLineArgsLocalClientCommand import (
                RelayLineArgsLocalClientCommand
            )
            return RelayLineArgsLocalClientCommand(
                call_ctx,
                self.server_config,
                self.local_server,
            )
        raise RuntimeError
