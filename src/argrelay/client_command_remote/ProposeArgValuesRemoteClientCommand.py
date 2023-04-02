import socket

from argrelay.handler_response.ProposeArgValuesClientResponseHandler import ProposeArgValuesClientResponseHandler
from argrelay.misc_helper.ElapsedTime import ElapsedTime
from argrelay.relay_client.AbstractClientCommand import AbstractClientCommand
from argrelay.runtime_context.InputContext import InputContext
from argrelay.runtime_data.ConnectionConfig import ConnectionConfig
from argrelay.server_spec.const_int import PROPOSE_ARG_VALUES_PATH


class ProposeArgValuesRemoteClientCommand(AbstractClientCommand):
    """
    This class is supposed to derive from :class:`AbstractRemoteClientCommand`, but it avoids it for perf reasons.

    See `completion_perf_notes.md`.

    Importing everything from `AbstractRemoteClientCommand` slows down startup and responses on `Tab` requests.

    Performance is not critical for other client commands
    (e.g. `DESCRIBE_LINE_ARGS_PATH` or `RELAY_LINE_ARGS_PATH`).

    Because `Tab`-completion is latency-sensitive, `PROPOSE_ARG_VALUES_PATH` command uses this specialized client.
    The drawback is that it also requires extra maintenance/testing.
    """

    # TODO: Provide test coverage for this special implementation.

    def __init__(
        self,
        connection_config: ConnectionConfig,
    ):
        super().__init__(
            ProposeArgValuesClientResponseHandler(),
        )
        self.connection_config = connection_config
        self.server_path = PROPOSE_ARG_VALUES_PATH

    def execute_command(self, input_ctx: InputContext):

        s = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )

        s.connect((
            self.connection_config.server_host_name,
            self.connection_config.server_port_number,
        ))

        request_body_str = (f"""\
{{
    "command_line": "{input_ctx.command_line}",
    "cursor_cpos": {input_ctx.cursor_cpos},
    "comp_type": "{input_ctx.comp_type.name}",
    "is_debug_enabled": "{'true' if input_ctx.is_debug_enabled else 'false'}"
}}
""")
        request_body_len = len(request_body_str.encode())

        request_str = (f"""\
POST {self.server_path} HTTP/1.1\r
Content-Type: application/json\r
Content-Length: {request_body_len}\r
Connection: close\r
\r
{request_body_str}
""")
        ElapsedTime.measure("before_request")

        s.sendall(request_str.encode())
        response_str = self.recvall(s).decode()

        ElapsedTime.measure("after_request")

        # First line, second space-delimited substring:
        # HTTP/1.1 200 OK\r\n
        response_status_line = response_str[:response_str.find("\r")]
        first_space_cpos = response_status_line.find(" ")
        response_status_code = int(
            response_status_line[first_space_cpos + 1:first_space_cpos + 1 + 3]
        )
        # Content after headers (after empty line):
        content_cpos = response_str.find("\r\n\r\n") + 4
        if content_cpos < len(response_str):
            response_body_str = response_str[content_cpos:]
        else:
            response_body_str = ""

        ElapsedTime.measure("after_deserialization")

        try:
            if response_status_code == 200:
                self.response_handler.handle_response({
                    "arg_values": response_body_str,
                })
            else:
                raise RuntimeError
        finally:
            ElapsedTime.measure("after_handle_response")

    # noinspection SpellCheckingInspection
    @staticmethod
    def recvall(s):
        bytes_parts = []
        while True:
            bytes_part = s.recv(1000)
            if not bytes_part:
                break
            bytes_parts.append(bytes_part)
        return b"".join(bytes_parts)
