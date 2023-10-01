class AbstractClientResponseHandler:

    def __init__(
        self,
    ):
        pass

    def handle_response(
        self,
        response_dict: dict,
    ):
        raise NotImplementedError
