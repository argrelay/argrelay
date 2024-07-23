from argrelay.enum_desc.ClientExitCode import ClientExitCode
from argrelay.enum_desc.ProcRole import ProcRole
from argrelay.relay_client.ClientCommandAbstract import ClientCommandAbstract
from argrelay.server_spec.CallContext import CallContext


class ClientCommandRemoteAbstract(ClientCommandAbstract):

    def __init__(
        self,
        call_ctx: CallContext,
        proc_role: ProcRole,
    ):
        super().__init__(
            call_ctx,
        )
        self.proc_role = proc_role

    @staticmethod
    def raise_error(
        status_code: int,
    ):
        raise RuntimeError(f"server response status_code: {status_code}")

    def execute_command(
        self,
    ):
        """
        Basic implementation of connection with single server.

        FS_93_18_57_91 client fail over is implemented in derived `ClientCommandRemoteWorkerAbstract` class.
        """
        try:
            self._execute_remotely()
        except (
            ConnectionError,
            ConnectionRefusedError,
        ) as e:
            if self.proc_role is ProcRole.ChildProcWorker:
                # tell parent what happened (let parent talk the rest):
                exit(ClientExitCode.ConnectionError.value)
            else:
                raise e

    def _execute_remotely(
        self,
    ):
        pass
