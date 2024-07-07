from argrelay.client_pipeline.BytesSrcAbstract import BytesSrcAbstract


class BytesSrcSender(BytesSrcAbstract):

    def __init__(
        self,
        w_pipe_end: "typing.BinaryIO",
    ):
        super().__init__(
        )
        self.w_pipe_end: "typing.BinaryIO" = w_pipe_end

    def accept_bytes(
        self,
        given_bytes: bytes,
    ):
        self.w_pipe_end.write(given_bytes)
