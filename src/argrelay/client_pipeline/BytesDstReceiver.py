from argrelay.client_pipeline.BytesHandlerAbstract import BytesHandlerAbstract
from argrelay.enum_desc.ClientExitCode import ClientExitCode
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
            client_exit_code = ClientExitCode(get_child_exit_code())
            exc_message = f"child exit_code: {client_exit_code} = {client_exit_code.name}"
            if client_exit_code is ClientExitCode.ConnectionError:
                raise ConnectionError(exc_message)
            else:
                raise RuntimeError(exc_message)

    def handle_bytes(
        self,
        given_bytes: bytes,
    ):
        self.bytes_handler.handle_bytes(given_bytes)
