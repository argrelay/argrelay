from argrelay.client_command_local.AbstractLocalClientCommand import AbstractLocalClientCommand
from argrelay.handler_request.ProposeArgValuesServerRequestHandler import ProposeArgValuesServerRequestHandler
from argrelay.handler_response.ProposeArgValuesClientResponseHandler import ProposeArgValuesClientResponseHandler
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_data.ServerConfig import ServerConfig


class ProposeArgValuesLocalClientCommand(AbstractLocalClientCommand):

    def __init__(
        self,
        server_config: ServerConfig,
        local_server: LocalServer,
    ):
        super().__init__(
            server_config = server_config,
            local_server = local_server,
            request_handler = ProposeArgValuesServerRequestHandler(local_server),
            response_handler = ProposeArgValuesClientResponseHandler(),
        )
