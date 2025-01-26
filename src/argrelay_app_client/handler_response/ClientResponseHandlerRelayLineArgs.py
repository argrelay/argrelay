from typing import Type

from argrelay_api_plugin_abstract.AbstractPlugin import import_plugin_class
from argrelay_api_plugin_server_abstract.DelegatorAbstract import DelegatorAbstract
from argrelay_api_server_cli.schema_response.InvocationInput import InvocationInput
from argrelay_api_server_cli.schema_response.InvocationInputSchema import invocation_input_desc
from argrelay_app_client.handler_response.ClientResponseHandlerAbstract import ClientResponseHandlerAbstract
from argrelay_lib_root.misc_helper_common.ElapsedTime import ElapsedTime


class ClientResponseHandlerRelayLineArgs(ClientResponseHandlerAbstract):

    def __init__(
        self,
    ):
        super().__init__(
        )

    def handle_response(
        self,
        response_dict: dict,
    ):
        invocation_input: InvocationInput = invocation_input_desc.dict_schema.load(response_dict)
        ElapsedTime.measure("after_object_creation")
        plugin_class: Type[DelegatorAbstract] = import_plugin_class(invocation_input.delegator_plugin_entry)
        plugin_class.invoke_action(invocation_input)
