from argrelay.handler_request.AbstractServerRequestHandler import AbstractServerRequestHandler
from argrelay.handler_response.AbstractClientResponseHandler import AbstractClientResponseHandler
from argrelay.misc_helper.ElapsedTime import ElapsedTime
from argrelay.relay_client.AbstractClientCommand import AbstractClientCommand
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InputContext import InputContext
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_data.ServerConfig import ServerConfig


class AbstractLocalClientCommand(AbstractClientCommand):
    server_config: ServerConfig
    local_server: LocalServer
    request_handler: AbstractServerRequestHandler
    response_dict: dict
    interp_ctx: InterpContext

    def __init__(
        self,
        server_config: ServerConfig,
        local_server: LocalServer,
        request_handler: AbstractServerRequestHandler,
        response_handler: AbstractClientResponseHandler,
    ):
        super().__init__(
            response_handler,
        )
        self.server_config = server_config
        self.local_server = local_server
        self.request_handler = request_handler

    def execute_command(self, input_ctx: InputContext):
        self.response_dict = self.request_handler.handle_request(input_ctx)
        ElapsedTime.measure("before_sending_response")
        self.response_handler.handle_response(self.response_dict)
        ElapsedTime.measure("after_handle_response")

        # `AbstractLocalClientCommand`'s feature: expose `InterpContext` used by the server:
        self.interp_ctx = self.request_handler.interp_ctx
