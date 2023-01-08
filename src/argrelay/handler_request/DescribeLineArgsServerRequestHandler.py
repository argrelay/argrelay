from argrelay.handler_request.AbstractServerRequestHandler import AbstractServerRequestHandler
from argrelay.meta_data.CompType import CompType
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InputContext import InputContext


class DescribeLineArgsServerRequestHandler(AbstractServerRequestHandler):

    def __init__(
        self,
        local_server: LocalServer,
    ):
        super().__init__(
            local_server = local_server
        )

    def handle_request(self, input_ctx: InputContext) -> dict:
        assert input_ctx.comp_type == CompType.DescribeArgs

        self.interpret_command(self.local_server, input_ctx)

        # TODO: Print to stdout/stderr on client side. Send back data instead:
        self.interp_ctx.print_help()
        return {}
