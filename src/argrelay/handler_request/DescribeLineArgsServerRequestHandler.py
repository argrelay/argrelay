from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.handler_request.AbstractServerRequestHandler import AbstractServerRequestHandler
from argrelay.misc_helper_common.ElapsedTime import ElapsedTime
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.schema_response.InterpResult import InterpResult
from argrelay.schema_response.InterpResultSchema import (
    interp_result_desc,
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
        assert call_ctx.server_action is ServerAction.DescribeLineArgs

        self.interpret_command(self.local_server, call_ctx)
        ElapsedTime.measure("after_interpret_command")

        input_object = InterpResult(
            arg_values = self.interp_ctx.comp_suggestions,
            all_tokens = self.interp_ctx.parsed_ctx.all_tokens,
            consumed_tokens = self.interp_ctx.consumed_tokens,
            envelope_containers = self.interp_ctx.envelope_containers,
            tan_token_ipos = self.interp_ctx.parsed_ctx.tan_token_ipos,
            tan_token_l_part = self.interp_ctx.parsed_ctx.tan_token_l_part,
        )
        response_dict = interp_result_desc.dict_schema.dump(input_object)

        return response_dict
