from typing import Type

from argrelay.handler_response.AbstractClientResponseHandler import AbstractClientResponseHandler
from argrelay.invocation_plugin.AbstractInvocator import AbstractInvocator
from argrelay.invocation_plugin.InvocationInput import InvocationInput
from argrelay.misc_helper.AbstractPlugin import import_plugin_class
from argrelay.schema_response.InvocationInputSchema import invocation_input_desc


class RelayLineArgsClientResponseHandler(AbstractClientResponseHandler):

    def __init__(
        self,
    ):
        super().__init__(
        )

    def handle_response(self, response_dict: dict):
        invocation_input: InvocationInput = invocation_input_desc.object_schema.load(response_dict)
        plugin_class: Type[AbstractInvocator] = import_plugin_class(invocation_input.invocator_plugin_entry)
        plugin_class.invoke_action(invocation_input)

