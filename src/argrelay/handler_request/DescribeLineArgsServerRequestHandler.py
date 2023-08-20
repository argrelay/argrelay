from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.handler_request.AbstractServerRequestHandler import AbstractServerRequestHandler
from argrelay.misc_helper.ElapsedTime import ElapsedTime
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.schema_response.InterpResultSchema import (
    interp_result_desc,
    envelope_containers_,
    all_tokens_,
    consumed_tokens_,
)
from argrelay.server_spec.CallContext import CallContext


class DescribeLineArgsServerRequestHandler(AbstractServerRequestHandler):

    def __init__(
        self,
        local_server: LocalServer,
    ):
        super().__init__(
            local_server = local_server,
        )

    def handle_request(
        self,
        call_ctx: CallContext,
    ) -> dict:
        assert call_ctx.server_action == ServerAction.DescribeLineArgs

        self.interpret_command(self.local_server, call_ctx)
        ElapsedTime.measure("after_interpret_command")

        response_dict = interp_result_desc.dict_schema.dump({
            all_tokens_: self.interp_ctx.parsed_ctx.all_tokens,
            consumed_tokens_: self.interp_ctx.consumed_tokens,
            envelope_containers_: self.interp_ctx.envelope_containers,
        })
        return response_dict
