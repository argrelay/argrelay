from argrelay.api_int.const_int import DESCRIBE_LINE_ARGS_PATH
from argrelay.relay_client.command_impl.AbstractCommand import AbstractCommand


class DescribeLineArgsCommand(AbstractCommand):

    def __init__(self):
        super().__init__(
            server_path = DESCRIBE_LINE_ARGS_PATH,
            # TODO:
            response_schema = None,
        )
