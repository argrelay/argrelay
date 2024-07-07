from argrelay.client_pipeline.BytesHandlerAbstract import BytesHandlerAbstract


class BytesHandlerTextProposeArgValuesOptimized(BytesHandlerAbstract):

    def __init__(
        self,
    ):
        super().__init__(
        )

    def handle_bytes(
        self,
        given_bytes: bytes,
    ):
        # For (default) "text/plain" response, proposed (new-line-separated) values are directly in the body:
        print(given_bytes.decode())
