from argrelay.client_command.AbstractCommand import AbstractCommand
from argrelay.server_spec.const_int import DESCRIBE_LINE_ARGS_PATH


class DescribeLineArgsCommand(AbstractCommand):

    def __init__(self):
        super().__init__(
            server_path = DESCRIBE_LINE_ARGS_PATH,
            # TODO: define data to be returned back from server to explain current command line interpretation:
            response_schema = None,
        )
