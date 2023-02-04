from argrelay.client_command_remote.AbstractRemoteClientCommand import AbstractRemoteClientCommand
from argrelay.handler_response.RelayLineArgsClientResponseHandler import RelayLineArgsClientResponseHandler
from argrelay.runtime_data.ConnectionConfig import ConnectionConfig
from argrelay.schema_response.InvocationInputSchema import invocation_input_desc
from argrelay.server_spec.const_int import RELAY_LINE_ARGS_PATH


class RelayLineArgsRemoteClientCommand(AbstractRemoteClientCommand):

    def __init__(
        self,
        connection_config: ConnectionConfig,
    ):
        super().__init__(
            server_path = RELAY_LINE_ARGS_PATH,
            connection_config = connection_config,
            response_handler = RelayLineArgsClientResponseHandler(),
            response_schema = invocation_input_desc.dict_schema,
        )
