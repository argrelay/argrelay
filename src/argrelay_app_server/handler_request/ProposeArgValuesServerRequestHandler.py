from argrelay_api_server_cli.schema_response.ArgValuesSchema import arg_values_
from argrelay_api_server_cli.server_spec.CallContext import CallContext
from argrelay_app_server.handler_request.AbstractServerRequestHandler import AbstractServerRequestHandler
from argrelay_app_server.relay_server.LocalServer import LocalServer
from argrelay_lib_root.enum_desc.ServerAction import ServerAction
from argrelay_lib_root.misc_helper_common.ElapsedTime import ElapsedTime


class ProposeArgValuesServerRequestHandler(AbstractServerRequestHandler):

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
        assert call_ctx.server_action is ServerAction.ProposeArgValues
        self._store_usage_stats_entry(call_ctx)

        self.interpret_command(self.local_server, call_ctx)
        ElapsedTime.measure("after_interpret_command")

        return {
            arg_values_: self.interp_ctx.propose_arg_values()
        }
