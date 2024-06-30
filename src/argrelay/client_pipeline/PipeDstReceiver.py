import typing

from argrelay.client_pipeline.BytesHandlerAbstract import BytesHandlerAbstract
from argrelay.relay_client.proc_spinner import spinner_main, child_stdout_chunks


class PipeDstReceiver:

    def __init__(
        self,
        bytes_handler: BytesHandlerAbstract,
        # TODO: review names:
        child_pid,
        pipe_dst: typing.BinaryIO,
        client_config,
        shell_ctx,
    ):
        super().__init__(
        )
        self.bytes_handler = bytes_handler
        self.child_pid = child_pid
        self.pipe_dst: typing.BinaryIO = pipe_dst
        self.client_config = client_config
        self.shell_ctx = shell_ctx

    def receive_bytes(
        self,
    ):
        spinner_main(
            self.child_pid,
            self.pipe_dst,
            self.client_config,
            self.shell_ctx,
        )
        # TODO: Ensure child exited successfully:
        self.handle_bytes(b"".join(child_stdout_chunks))

    def handle_bytes(
        self,
        given_bytes: bytes,
    ):
        self.bytes_handler.handle_bytes(given_bytes)
