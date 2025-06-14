from __future__ import annotations

from typing import Union

from argrelay_api_server_cli.server_spec.CallContext import CallContext
from argrelay_app_client.handler_response.ClientResponseHandlerAbstract import (
    ClientResponseHandlerAbstract,
)
from argrelay_app_client.relay_client.ClientCommandAbstract import ClientCommandAbstract
from argrelay_app_server.handler_request.AbstractServerRequestHandler import (
    AbstractServerRequestHandler,
)
from argrelay_app_server.relay_server.LocalServer import LocalServer
from argrelay_app_server.runtime_context.InterpContext import InterpContext
from argrelay_lib_root.misc_helper_common.ElapsedTime import ElapsedTime


class ClientCommandLocal(ClientCommandAbstract):

    def __init__(
        self,
        call_ctx: CallContext,
        client_response_handler: ClientResponseHandlerAbstract,
        local_server: LocalServer,
        server_request_handler: AbstractServerRequestHandler,
    ):
        super().__init__(
            call_ctx,
        )
        self.client_response_handler: ClientResponseHandlerAbstract = (
            client_response_handler
        )
        self.local_server: LocalServer = local_server
        self.server_request_handler: AbstractServerRequestHandler = (
            server_request_handler
        )
        self.response_dict: Union[dict, None] = None
        self.interp_ctx: Union[InterpContext, None] = None

    def execute_command(
        self,
    ):
        self.response_dict = self.server_request_handler.handle_request(self.call_ctx)
        ElapsedTime.measure("before_sending_response")
        self.client_response_handler.handle_response(self.response_dict)
        ElapsedTime.measure("after_handle_response")

        # `ClientCommandLocal`'s feature: expose `InterpContext` used by the server:
        self.interp_ctx = self.server_request_handler.interp_ctx
