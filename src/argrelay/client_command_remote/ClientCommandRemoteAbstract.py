from argrelay.client_command_remote.exception_utils import ServerResponseError, print_full_stack_trace
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
        raise ServerResponseError(f"server response status_code: {status_code}")

    def execute_command(
        self,
    ):
        self._execute_single_call()

    def _execute_single_call(
        self,
    ):
        """
        Basic implementation of remote call to a single server.

        See `ClientCommandRemoteWorkerAbstract._execute_multiple_calls` for alternative.
        """
        try:
            self._execute_remote_call()
        except (
            ConnectionError,
            ConnectionRefusedError,
        ) as e:
            self._handle_exception_with_exit_code(
                False,
                e,
                ClientExitCode.ConnectionError.value,
            )
        except ServerResponseError as e:
            self._handle_exception_with_exit_code(
                True,
                e,
                ClientExitCode.ServerError.value,
            )

    def _handle_exception_with_exit_code(
        self,
        print_stack_trace_on_exit,
        exception_obj,
        exit_code,
    ):
        """
        Raise exception or exit with exit code depending on `ProcRole`.
        """
        if (
            self.proc_role.is_worker_proc
            and
            # FS_36_17_84_44 check_env: do not exit:
            self.proc_role is not ProcRole.CheckEnvWorker
        ):
            if print_stack_trace_on_exit:
                print_full_stack_trace(exception_obj)
            # Tell parent what happened (let parent talk the rest):
            exit(exit_code)
        else:
            raise exception_obj

    def _execute_remote_call(
        self,
    ):
        pass
