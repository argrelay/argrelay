from argrelay.handler_request.AbstractServerRequestHandler import AbstractServerRequestHandler
from argrelay.meta_data.CompType import CompType
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InputContext import InputContext


class ProposeArgValuesServerRequestHandler(AbstractServerRequestHandler):

    def __init__(
        self,
        local_server: LocalServer,
    ):
        super().__init__(
            local_server = local_server
        )

    def handle_request(self, input_ctx: InputContext) -> dict:
        assert input_ctx.comp_type != CompType.DescribeArgs
        assert input_ctx.comp_type != CompType.InvokeAction

        self.interpret_command(self.local_server, input_ctx)

        return {
            "arg_values": self.interp_ctx.propose_arg_values()
        }