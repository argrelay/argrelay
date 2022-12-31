from argrelay.client_command.AbstractCommand import AbstractCommand
from argrelay.data_schema.ArgValuesSchema import arg_values_desc
from argrelay.server_spec.const_int import PROPOSE_ARG_VALUES_PATH


class ProposeArgValuesCommand(AbstractCommand):

    def __init__(self):
        super().__init__(
            server_path = PROPOSE_ARG_VALUES_PATH,
            response_schema = arg_values_desc.object_schema,
        )
