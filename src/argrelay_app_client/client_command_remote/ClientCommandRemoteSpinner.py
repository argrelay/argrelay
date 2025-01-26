from argrelay_api_server_cli.server_spec.CallContext import CallContext
from argrelay_app_client.client_command_remote.ClientCommandRemoteAbstract import ClientCommandRemoteAbstract
from argrelay_app_client.client_pipeline.BytesDstReceiver import BytesDstReceiver
from argrelay_app_client.client_pipeline.BytesHandlerAbstract import BytesHandlerAbstract
from argrelay_lib_root.enum_desc.ProcRole import ProcRole


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
