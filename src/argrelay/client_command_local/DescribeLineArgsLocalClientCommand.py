from argrelay.client_command_local.AbstractLocalClientCommand import AbstractLocalClientCommand
from argrelay.handler_request.DescribeLineArgsServerRequestHandler import DescribeLineArgsServerRequestHandler
from argrelay.handler_response.DescribeLineArgsClientResponseHandler import DescribeLineArgsClientResponseHandler
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.server_spec.CallContext import CallContext


class DescribeLineArgsLocalClientCommand(AbstractLocalClientCommand):

    def __init__(
        self,
        call_ctx: CallContext,
        local_server: LocalServer,
    ):
        super().__init__(
            call_ctx = call_ctx,
            client_response_handler = DescribeLineArgsClientResponseHandler(),
            local_server = local_server,
            server_request_handler = DescribeLineArgsServerRequestHandler(local_server),
        )
