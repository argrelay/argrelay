from argrelay.client_command_local.ClientCommandLocal import ClientCommandLocal
from argrelay.enum_desc.ProcRole import ProcRole
from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.misc_helper_common.ElapsedTime import ElapsedTime
from argrelay.relay_client.ClientCommandFactoryAbstract import (
    ClientCommandFactoryAbstract,
    select_client_response_handler,
)
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_data.PluginConfig import PluginConfig
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.schema_config_core_server.ServerConfigSchema import server_config_desc
from argrelay.schema_config_plugin.PluginConfigSchema import plugin_config_desc
from argrelay.server_spec.CallContext import CallContext


class ClientCommandFactoryLocal(ClientCommandFactoryAbstract):
    local_server: LocalServer = None
    """
    This instance of `LocalServer` allows reusing server for multiple `ClientLocal` invocation in tests.
    For example, to avoid re-loading TD_38_03_48_51 large data sets.
    """

    def __init__(self):
        self._start_local_server()

    def _start_local_server(self):
        if not ClientCommandFactoryLocal.local_server:
            self.server_config: ServerConfig = server_config_desc.obj_from_default_file()
            self.plugin_config: PluginConfig = plugin_config_desc.obj_from_default_file()
            ElapsedTime.measure("after_server_config_load")
            ClientCommandFactoryLocal.local_server = LocalServer(
                self.server_config,
                self.plugin_config,
            )
            ClientCommandFactoryLocal.local_server.start_local_server()
            ElapsedTime.measure("after_local_server_start")
        else:
            self.server_config: ServerConfig = ClientCommandFactoryLocal.local_server.server_config

    def create_command(
        self,
        call_ctx: CallContext,
    ) -> ClientCommandLocal:
        return ClientCommandLocal(
            call_ctx = call_ctx,
            client_response_handler = select_client_response_handler(
                ProcRole.SoleProcWorker,
                call_ctx.server_action,
            ),
            local_server = self.local_server,
            server_request_handler = select_local_server_request_handler(
                call_ctx.server_action,
                self.local_server,
            ),
        )


def select_local_server_request_handler(
    server_action: ServerAction,
    local_server: LocalServer,
):
    if server_action is ServerAction.ProposeArgValues:
        from argrelay.handler_request.ProposeArgValuesServerRequestHandler import (
            ProposeArgValuesServerRequestHandler,
        )
        return ProposeArgValuesServerRequestHandler(local_server)
    if server_action is ServerAction.DescribeLineArgs:
        from argrelay.handler_request.DescribeLineArgsServerRequestHandler import (
            DescribeLineArgsServerRequestHandler,
        )
        return DescribeLineArgsServerRequestHandler(local_server)
    if server_action is ServerAction.RelayLineArgs:
        from argrelay.handler_request.RelayLineArgsServerRequestHandler import (
            RelayLineArgsServerRequestHandler,
        )
        return RelayLineArgsServerRequestHandler(local_server)
    raise RuntimeError
