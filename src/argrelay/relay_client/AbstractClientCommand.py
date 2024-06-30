from argrelay.server_spec.CallContext import CallContext


class AbstractClientCommand:

    def __init__(
        self,
        call_ctx: CallContext,
    ):
        self.call_ctx: CallContext = call_ctx

    def execute_command(
        self,
    ):
        pass
