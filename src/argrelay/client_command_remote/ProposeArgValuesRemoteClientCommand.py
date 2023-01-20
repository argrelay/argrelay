from argrelay.client_command_remote.AbstractRemoteClientCommand import AbstractRemoteClientCommand
from argrelay.handler_response.ProposeArgValuesClientResponseHandler import ProposeArgValuesClientResponseHandler
from argrelay.runtime_data.ConnectionConfig import ConnectionConfig
from argrelay.schema_response.ArgValuesSchema import arg_values_desc
from argrelay.server_spec.const_int import PROPOSE_ARG_VALUES_PATH


class ProposeArgValuesRemoteClientCommand(AbstractRemoteClientCommand):

    def __init__(
        self,
        connection_config: ConnectionConfig,
    ):
        super().__init__(
            server_path = PROPOSE_ARG_VALUES_PATH,
            connection_config = connection_config,
            response_handler = ProposeArgValuesClientResponseHandler(),
            response_schema = arg_values_desc.dict_schema,
        )
