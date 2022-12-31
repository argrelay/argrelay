from argrelay.api_int.const_int import RELAY_LINE_ARGS_PATH
from argrelay.relay_client.command_impl.AbstractCommand import AbstractCommand


class RelayLineArgsCommand(AbstractCommand):

    def __init__(self):
        super().__init__(
            server_path = RELAY_LINE_ARGS_PATH,
            # TODO: define data to be returned back from server to execute function on client side:
            response_schema = None,
        )
