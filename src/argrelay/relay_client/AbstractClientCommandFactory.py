from argrelay.relay_client import AbstractClientCommand
from argrelay.server_spec.CallContext import CallContext


class AbstractClientCommandFactory:

    def create_command(
        self,
        call_ctx: CallContext,
    ) -> AbstractClientCommand:
        pass
