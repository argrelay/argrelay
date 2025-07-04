from argrelay_api_server_cli.schema_response.ArgValues import ArgValues
from argrelay_api_server_cli.schema_response.ArgValuesSchema import arg_values_desc
from argrelay_app_client.handler_response.ClientResponseHandlerAbstract import (
    ClientResponseHandlerAbstract,
)
from argrelay_lib_root.misc_helper_common.ElapsedTime import ElapsedTime


class ClientResponseHandlerProposeArgValues(ClientResponseHandlerAbstract):
    """
    This handler is supposed to be used by non-optimized implementations like:
    *   `ClientCommandLocal`
    *   `ClientCommandRemoteWorkerJson`

    Optimized `ClientCommandRemoteWorkerTextProposeArgValuesOptimized` prints suggestion without using marshmallow `Schema`-s.
    """

    def __init__(
        self,
    ):
        super().__init__()

    def handle_response(
        self,
        response_dict: dict,
    ):
        arg_values: ArgValues = arg_values_desc.dict_schema.load(response_dict)
        ElapsedTime.measure("after_object_creation")
        self.render_values(arg_values)

    @staticmethod
    def render_values(
        arg_values: ArgValues,
    ):
        print("\n".join(arg_values.arg_values))
