import json

from argrelay.client_pipeline.BytesHandlerAbstract import BytesHandlerAbstract
from argrelay.handler_response.ClientResponseHandlerAbstract import ClientResponseHandlerAbstract
from argrelay.misc_helper_common.ElapsedTime import ElapsedTime


class BytesHandlerJson(BytesHandlerAbstract):

    def __init__(
        self,
        client_response_handler: ClientResponseHandlerAbstract,
    ):
        super().__init__(
        )
        self.client_response_handler = client_response_handler

    def handle_bytes(
        self,
        given_bytes: bytes,
    ):
        # Leave both object creation and validation via schemas to `client_response_handler`.
        # Just deserialize into dict here:
        response_dict = json.loads(given_bytes.decode())
        ElapsedTime.measure("after_deserialization")
        self.client_response_handler.handle_response(response_dict)
