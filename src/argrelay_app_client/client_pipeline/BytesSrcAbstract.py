class BytesSrcAbstract:

    def __init__(
        self,
    ):
        super().__init__()

    def accept_bytes(
        self,
        given_bytes: bytes,
    ):
        # Implement in derived class:
        raise NotImplementedError()
