import signal
from dataclasses import asdict

from argrelay.client_command_remote.ClientCommandRemoteAbstract import ClientCommandRemoteAbstract
from argrelay.client_pipeline.BytesSrcAbstract import BytesSrcAbstract
from argrelay.enum_desc.ProcRole import ProcRole
from argrelay.misc_helper_common import eprint
from argrelay.misc_helper_common.ElapsedTime import ElapsedTime
from argrelay.runtime_data.ConnectionConfig import ConnectionConfig
from argrelay.schema_request.CallContextSchema import call_context_desc
from argrelay.server_spec.CallContext import CallContext
from argrelay.server_spec.const_int import BASE_URL_FORMAT

has_error_happened = False


def _signal_handler(signal_number, signal_frame):
    if signal_number == signal.SIGALRM:
        # Import hanged:
        eprint("ERROR: `import` hanged - see: https://github.com/argrelay/argrelay/issues/89")
        global has_error_happened
        has_error_happened = True


class ClientCommandRemoteWorkerJson(ClientCommandRemoteAbstract):

    def __init__(
        self,
        call_ctx: CallContext,
        proc_role: ProcRole,
        connection_config: ConnectionConfig,
        bytes_src: BytesSrcAbstract,
    ):
        super().__init__(
            call_ctx,
            proc_role,
        )
        self.connection_config: ConnectionConfig = connection_config
        self.bytes_src: BytesSrcAbstract = bytes_src

    def _execute_remotely(
        self,
    ):
        server_url = BASE_URL_FORMAT.format(**asdict(self.connection_config)) + f"{self.call_ctx.server_action.value}"
        headers_dict = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        # NOTE: So far, single `CallContextSchema` is reused for all client requests:
        request_json = call_context_desc.dict_schema.dumps(self.call_ctx)
        ElapsedTime.measure("before_request")

        # TODO: TODO_30_69_19_14: infinite spinner:
        #     There is a bug - if a child is used, it deadlocks occasionally while importing `requests`:
        #     https://github.com/argrelay/argrelay/issues/89
        #     The workaround is to abort (Ctrl+C) and retry - but this is annoying.
        # Attempt to detect hanging import by setting an alarm at least (not resolving it yet):
        signal.signal(signal.SIGALRM, _signal_handler)
        signal.alarm(1)
        import requests
        signal.alarm(0)

        try:
            response_obj = requests.post(
                server_url,
                headers = headers_dict,
                data = request_json,
            )
        except requests.exceptions.ConnectionError as e:
            # translate to builtin:
            raise ConnectionError(e)

        ElapsedTime.measure("after_request")
        try:
            if response_obj.ok:
                self.bytes_src.accept_bytes(response_obj.content)
            else:
                self.raise_error(response_obj.status_code)
        finally:
            ElapsedTime.measure("after_handle_response")
