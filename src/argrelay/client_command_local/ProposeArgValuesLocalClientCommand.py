from argrelay.client_command_local.AbstractLocalClientCommand import AbstractLocalClientCommand
from argrelay.handler_request.ProposeArgValuesServerRequestHandler import ProposeArgValuesServerRequestHandler
from argrelay.handler_response.ProposeArgValuesClientResponseHandler import ProposeArgValuesClientResponseHandler
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.server_spec.CallContext import CallContext


class ProposeArgValuesLocalClientCommand(AbstractLocalClientCommand):

    def __init__(
        self,
        call_ctx: CallContext,
        local_server: LocalServer,
    ):
        super().__init__(
            call_ctx = call_ctx,
            client_response_handler = ProposeArgValuesClientResponseHandler(),
            local_server = local_server,
            server_request_handler = ProposeArgValuesServerRequestHandler(local_server),
        )
