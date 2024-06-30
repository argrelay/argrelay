import sys

from argrelay.client_pipeline.PipeSrcAbstract import PipeSrcAbstract


class PipeSrcSender(PipeSrcAbstract):

    def __init__(
        self,
        pipe_src: "typing.BinaryIO",
    ):
        super().__init__(
        )
        self.pipe_src: "typing.BinaryIO" = pipe_src

    def accept_bytes(
        self,
        given_bytes: bytes,
    ):
        self.pipe_src.write(given_bytes)
