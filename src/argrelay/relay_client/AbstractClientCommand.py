from argrelay.handler_response.AbstractClientResponseHandler import AbstractClientResponseHandler
from argrelay.runtime_context.InputContext import InputContext


class AbstractClientCommand:

    def __init__(
        self,
        response_handler: AbstractClientResponseHandler,
    ):
        self.response_handler: AbstractClientResponseHandler = response_handler

    def execute_command(self, input_ctx: InputContext):
        pass
