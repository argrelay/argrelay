from argrelay.handler_request.AbstractServerRequestHandler import AbstractServerRequestHandler
from argrelay.handler_response.AbstractClientResponseHandler import AbstractClientResponseHandler
from argrelay.misc_helper_common.ElapsedTime import ElapsedTime
from argrelay.relay_client.AbstractClientCommand import AbstractClientCommand
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.server_spec.CallContext import CallContext


class AbstractLocalClientCommand(AbstractClientCommand):

    def __init__(
        self,
        call_ctx: CallContext,
        server_config: ServerConfig,
        local_server: LocalServer,
        request_handler: AbstractServerRequestHandler,
        response_handler: AbstractClientResponseHandler,
    ):
        super().__init__(
            response_handler,
        )
        self.call_ctx: CallContext = call_ctx
        self.server_config: ServerConfig = server_config
        self.local_server: LocalServer = local_server
        self.request_handler: AbstractServerRequestHandler = request_handler
        self.response_dict: dict
        self.interp_ctx: InterpContext

    def execute_command(
        self,
    ):
        self.response_dict = self.request_handler.handle_request(self.call_ctx)
        ElapsedTime.measure("before_sending_response")
        self.response_handler.handle_response(self.response_dict)
        ElapsedTime.measure("after_handle_response")

        # `AbstractLocalClientCommand`'s feature: expose `InterpContext` used by the server:
        self.interp_ctx = self.request_handler.interp_ctx
