from argrelay.client_pipeline.BytesHandlerAbstract import BytesHandlerAbstract
from argrelay.client_pipeline.BytesSrcAbstract import BytesSrcAbstract


class BytesSrcLocal(BytesSrcAbstract):

    def __init__(
        self,
        bytes_handler: BytesHandlerAbstract,
    ):
        super().__init__()
        self.bytes_handler = bytes_handler

    def accept_bytes(
        self,
        given_bytes: bytes,
    ):
        self.bytes_handler.handle_bytes(given_bytes)
