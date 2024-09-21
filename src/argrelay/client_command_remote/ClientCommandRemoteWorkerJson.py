import signal
from dataclasses import asdict

from argrelay.client_command_remote.ClientCommandRemoteWorkerAbstract import ClientCommandRemoteWorkerAbstract
from argrelay.misc_helper_common import eprint
from argrelay.misc_helper_common.ElapsedTime import ElapsedTime
from argrelay.schema_request.CallContextSchema import call_context_desc
from argrelay.server_spec.const_int import BASE_URL_FORMAT

has_error_happened = False


def _signal_handler(signal_number, signal_frame):
    if signal_number == signal.SIGALRM:
        # Import hanged:
        eprint("ERROR: `import` hanged, `Ctrl + C` and retry, details: https://github.com/argrelay/argrelay/issues/89")
        global has_error_happened
        has_error_happened = True


class ClientCommandRemoteWorkerJson(ClientCommandRemoteWorkerAbstract):

    def _execute_remote_call(
        self,
    ):
        server_url = BASE_URL_FORMAT.format(
            **asdict(self.curr_connection_config)
        ) + f"{self.call_ctx.server_action.value}"
        headers_dict = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        # NOTE: So far, single `CallContextSchema` is reused for all client requests:
        request_json = call_context_desc.dict_schema.dumps(self.call_ctx)
        request_bytes = request_json.encode()
        ElapsedTime.measure("before_request")

        # TODO: TODO_30_69_19_14: infinite spinner:
        #     There is a bug - if a child is used, it deadlocks occasionally while importing `requests`:
        #     https://github.com/argrelay/argrelay/issues/89
        #     The workaround is to abort (Ctrl+C) and retry - but this is annoying.
        # Attempt to detect hanging import by setting an alarm at least (not resolving it yet):
        signal.signal(signal.SIGALRM, _signal_handler)
        signal.alarm(1)
        import urllib3
        signal.alarm(0)

        try:
            response_obj = urllib3.request(
                "POST",
                server_url,
                headers = headers_dict,
                body = request_bytes,
                timeout = urllib3.util.Timeout(
                    connect = 5,
                    read = 60,
                ),
            )
        except urllib3.exceptions.MaxRetryError as e:
            # translate to builtin:
            raise ConnectionError(e)

        ElapsedTime.measure("after_request")
        try:
            if response_obj.status == 200:
                self.bytes_src.accept_bytes(response_obj.data)
            else:
                self.raise_error(response_obj.status)
        finally:
            ElapsedTime.measure("after_handle_response")
