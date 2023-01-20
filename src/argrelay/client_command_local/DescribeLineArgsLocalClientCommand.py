from argrelay.client_command_local.AbstractLocalClientCommand import AbstractLocalClientCommand
from argrelay.handler_request.DescribeLineArgsServerRequestHandler import DescribeLineArgsServerRequestHandler
from argrelay.handler_response.DescribeLineArgsClientResponseHandler import DescribeLineArgsClientResponseHandler
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_data.ServerConfig import ServerConfig


class DescribeLineArgsLocalClientCommand(AbstractLocalClientCommand):

    def __init__(
        self,
        server_config: ServerConfig,
        local_server: LocalServer,
    ):
        super().__init__(
            server_config = server_config,
            local_server = local_server,
            request_handler = DescribeLineArgsServerRequestHandler(local_server),
            response_handler = DescribeLineArgsClientResponseHandler(),
        )
