from argrelay.handler_response.AbstractClientResponseHandler import AbstractClientResponseHandler


class ProposeArgValuesClientResponseHandler(AbstractClientResponseHandler):

    def __init__(
        self,
    ):
        super().__init__(
        )

    # TODO: this does not look correct: server sends plain text (new-line-separated suggestions):
    def handle_response(self, response_dict: dict):
        print(response_dict["arg_values"])
