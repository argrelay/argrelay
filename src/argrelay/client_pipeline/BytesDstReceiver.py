import typing

from argrelay.client_pipeline.BytesHandlerAbstract import BytesHandlerAbstract
from argrelay.relay_client.proc_spinner import child_data_chunks
from argrelay.relay_client.proc_splitter import is_child_successful, get_child_exit_code


class BytesDstReceiver:

    def __init__(
        self,
        bytes_handler: BytesHandlerAbstract,
    ):
        super().__init__(
        )
        self.bytes_handler = bytes_handler

    def receive_bytes(
        self,
    ):
        if is_child_successful():
            self.handle_bytes(b"".join(child_data_chunks))
        else:
            raise RuntimeError(f"child exit_code: {get_child_exit_code()}")

    def handle_bytes(
        self,
        given_bytes: bytes,
    ):
        self.bytes_handler.handle_bytes(given_bytes)
