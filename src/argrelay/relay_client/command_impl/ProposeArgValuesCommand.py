from argrelay.api_int.const_int import PROPOSE_ARG_VALUES_PATH
from argrelay.api_int.data_schema.ArgValuesSchema import arg_values_desc
from argrelay.relay_client.command_impl.AbstractCommand import AbstractCommand


class ProposeArgValuesCommand(AbstractCommand):

    def __init__(self):
        super().__init__(
            server_path = PROPOSE_ARG_VALUES_PATH,
            response_schema = arg_values_desc.object_schema,
        )
