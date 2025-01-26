from argrelay_api_server_cli.server_spec.CallContext import CallContext


class ClientCommandAbstract:

    def __init__(
        self,
        call_ctx: CallContext,
    ):
        self.call_ctx: CallContext = call_ctx

    def execute_command(
        self,
    ):
        pass
