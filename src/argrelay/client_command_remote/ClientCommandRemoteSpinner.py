from argrelay.client_command_remote.ClientCommandRemoteAbstract import ClientCommandRemoteAbstract
from argrelay.client_pipeline.BytesDstReceiver import BytesDstReceiver
from argrelay.client_pipeline.BytesHandlerAbstract import BytesHandlerAbstract
from argrelay.server_spec.CallContext import CallContext


class ClientCommandRemoteSpinner(ClientCommandRemoteAbstract):
    """
    Command for `ProcRole.ParentProcSpinner` side.

    It does not make any remote request - it only processes data out of the pipe from `ProcRole.ChildProcWorker`.
    """

    def __init__(
        self,
        call_ctx: CallContext,
        bytes_handler: BytesHandlerAbstract,
    ):
        super().__init__(
            call_ctx,
        )
        self.bytes_dst = BytesDstReceiver(
            bytes_handler,
        )

    def execute_command(
        self,
    ):
        self.bytes_dst.receive_bytes()
