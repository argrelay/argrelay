from argrelay.client_spec.ShellContext import ShellContext
from argrelay.relay_client import AbstractClientCommand
from argrelay.server_spec.CallContext import CallContext


class AbstractClientCommandFactory:

    def create_command_by_server_path(
        self,
        call_ctx: CallContext,
    ) -> AbstractClientCommand:
        pass

    def create_command(
        self,
        shell_ctx: ShellContext,
    ):
        call_ctx = shell_ctx.create_call_context()
        return self.create_command_by_server_path(call_ctx)
