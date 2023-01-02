from argrelay.data_schema.ServerConfigSchema import server_config_desc
from argrelay.meta_data.ClientConfig import ClientConfig
from argrelay.meta_data.ServerConfig import ServerConfig
from argrelay.misc_helper.ElapsedTime import ElapsedTime
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InputContext import InputContext
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_context.ParsedContext import ParsedContext


class LocalClient:
    """
    Client local to server
    """

    @staticmethod
    def make_request(client_config: ClientConfig, input_ctx: InputContext) -> InterpContext:
        assert client_config.use_local_requests

        server_config: ServerConfig = server_config_desc.from_default_file()
        ElapsedTime.measure("after_server_config_load")

        local_server = LocalServer(server_config)
        local_server.start_local_server()
        ElapsedTime.measure("after_local_server_start")

        parsed_ctx = ParsedContext.from_instance(input_ctx)
        interp_ctx = InterpContext(
            parsed_ctx,
            server_config.static_data,
            server_config.interp_factories,
            local_server.mongo_client[server_config.mongo_config.database_name],
        )
        interp_ctx.interpret_command()
        ElapsedTime.measure("after_interp")

        interp_ctx.invoke_action()
        ElapsedTime.measure("after_request_processed")

        return interp_ctx
