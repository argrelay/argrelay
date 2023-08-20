from argrelay.handler_response.AbstractClientResponseHandler import AbstractClientResponseHandler


class AbstractClientCommand:

    def __init__(
        self,
        response_handler: AbstractClientResponseHandler,
    ):
        self.response_handler: AbstractClientResponseHandler = response_handler

    def execute_command(
        self,
    ):
        pass
