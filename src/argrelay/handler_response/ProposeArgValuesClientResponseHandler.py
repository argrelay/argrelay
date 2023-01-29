from argrelay.handler_response.AbstractClientResponseHandler import AbstractClientResponseHandler


class ProposeArgValuesClientResponseHandler(AbstractClientResponseHandler):

    def __init__(
        self,
    ):
        super().__init__(
        )

    def handle_response(self, response_dict: dict):
        print(response_dict["arg_values"])
