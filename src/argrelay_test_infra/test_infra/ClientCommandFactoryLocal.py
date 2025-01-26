from argrelay_api_server_cli.server_spec.CallContext import CallContext
from argrelay_app_client.client_command_local.ClientCommandLocal import ClientCommandLocal
from argrelay_app_client.relay_client.ClientCommandFactoryAbstract import (
    ClientCommandFactoryAbstract,
    select_client_response_handler,
)
from argrelay_app_server.relay_server.LocalServer import LocalServer
from argrelay_lib_root.enum_desc.ProcRole import ProcRole
from argrelay_lib_root.enum_desc.ServerAction import ServerAction
from argrelay_lib_root.misc_helper_common.ElapsedTime import ElapsedTime
from argrelay_schema_config_server.runtime_data_server_app.ServerConfig import ServerConfig
from argrelay_schema_config_server.runtime_data_server_plugin.PluginConfig import PluginConfig
from argrelay_schema_config_server.schema_config_server_app.ServerConfigSchema import server_config_desc
from argrelay_schema_config_server.schema_config_server_plugin.PluginConfigSchema import plugin_config_desc


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
        from argrelay_app_server.handler_request.ProposeArgValuesServerRequestHandler import (
            ProposeArgValuesServerRequestHandler,
        )
        return ProposeArgValuesServerRequestHandler(local_server)
    if server_action is ServerAction.DescribeLineArgs:
        from argrelay_app_server.handler_request.DescribeLineArgsServerRequestHandler import (
            DescribeLineArgsServerRequestHandler,
        )
        return DescribeLineArgsServerRequestHandler(local_server)
    if server_action is ServerAction.RelayLineArgs:
        from argrelay_app_server.handler_request.RelayLineArgsServerRequestHandler import (
            RelayLineArgsServerRequestHandler,
        )
        return RelayLineArgsServerRequestHandler(local_server)
    raise RuntimeError
