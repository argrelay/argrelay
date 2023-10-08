from argrelay.handler_response.AbstractClientResponseHandler import AbstractClientResponseHandler

perf_arg_values_ = "arg_values"
"""
This constant avoids import of similar `ArgValuesSchema.arg_values_` triggering `Schema` import which more than doubles
total round trip time for the client - see also `test_ProposeArgValuesRemoteClientCommand_imports_minimum`.
"""


class ProposeArgValuesClientResponseHandler(AbstractClientResponseHandler):

    def __init__(
        self,
    ):
        super().__init__(
        )

    def handle_response(self, response_dict: dict):
        print(response_dict[perf_arg_values_])
