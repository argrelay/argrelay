from argrelay.relay_client.ClientCommandAbstract import ClientCommandAbstract
from argrelay.server_spec.CallContext import CallContext


class ClientCommandRemoteAbstract(ClientCommandAbstract):

    def __init__(
        self,
        call_ctx: CallContext,
    ):
        super().__init__(
            call_ctx,
        )

    @staticmethod
    def raise_error(
        status_code: int,
    ):
        raise RuntimeError(f"server response status_code: {status_code}")
