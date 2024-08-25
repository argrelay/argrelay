from argrelay.client_command_remote.ClientCommandRemoteAbstract import ClientCommandRemoteAbstract
from argrelay.client_pipeline.BytesDstReceiver import BytesDstReceiver
from argrelay.client_pipeline.BytesHandlerAbstract import BytesHandlerAbstract
from argrelay.enum_desc.ProcRole import ProcRole
from argrelay.server_spec.CallContext import CallContext


class ClientCommandRemoteSpinner(ClientCommandRemoteAbstract):
    """
    Command for `ProcRole.ParentProcSpinner` side.

    It does not make any remote request - it only processes data out of the pipe from `ProcRole.ChildProcWorker`.
    """

    def __init__(
        self,
        call_ctx: CallContext,
        proc_role: ProcRole,
        bytes_handler: BytesHandlerAbstract,
    ):
        super().__init__(
            call_ctx,
            proc_role,
        )
        self.bytes_dst = BytesDstReceiver(
            bytes_handler,
        )

    def _execute_remote_call(
        self,
    ):
        """
        `ProcRole.ParentProcSpinner` receives data via pipe from `ProcRole.ChildProcWorker` or its exit code.
        """
        self.bytes_dst.receive_bytes()
