from argrelay.client_command_remote.AbstractRemoteClientCommand import AbstractRemoteClientCommand
from argrelay.handler_response.DescribeLineArgsClientResponseHandler import DescribeLineArgsClientResponseHandler
from argrelay.meta_data.ConnectionConfig import ConnectionConfig
from argrelay.server_spec.const_int import DESCRIBE_LINE_ARGS_PATH


class DescribeLineArgsRemoteClientCommand(AbstractRemoteClientCommand):

    def __init__(
        self,
        connection_config: ConnectionConfig,
    ):
        super().__init__(
            server_path = DESCRIBE_LINE_ARGS_PATH,
            connection_config = connection_config,
            response_handler = DescribeLineArgsClientResponseHandler(),
            # TODO: define data to be returned back from server to explain current command line interpretation:
            response_schema = None,
        )
