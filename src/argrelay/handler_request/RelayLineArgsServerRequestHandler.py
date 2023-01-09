import dataclasses

from argrelay.handler_request.AbstractServerRequestHandler import AbstractServerRequestHandler
from argrelay.plugin_invocator.AbstractInvocator import AbstractInvocator
from argrelay.plugin_invocator.InvocationInput import InvocationInput
from argrelay.meta_data.CompType import CompType
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InputContext import InputContext
from argrelay.schema_config_interp.DataObjectSchema import object_data_, data_object_desc
from argrelay.schema_config_interp.FunctionObjectDataSchema import invocator_plugin_id_, function_object_data_desc
from argrelay.schema_response.InvocationInputSchema import invocation_input_desc


class RelayLineArgsServerRequestHandler(AbstractServerRequestHandler):

    def __init__(
        self,
        local_server: LocalServer,
    ):
        super().__init__(
            local_server = local_server
        )

    def handle_request(self, input_ctx: InputContext) -> dict:
        assert input_ctx.comp_type == CompType.InvokeAction

        self.interpret_command(self.local_server, input_ctx)

        # The first object (`DataObjectSchema`) is assumed to be of
        # `ReservedObjectClass.ClassFunction` with `FunctionObjectDataSchema` for its `object_data`:
        function_object = self.interp_ctx.assigned_types_to_values_per_object[0]
        if object_data_ not in function_object:
            # TODO: Think how to pass info about failure.
            #       Maybe create an ErrorInvocatorPlugin and send data to client?
            #       At the moment, send some fake object:
            function_object = data_object_desc.dict_example
        invocator_plugin_id = function_object[object_data_][invocator_plugin_id_]
        invocator_plugin: AbstractInvocator = self.local_server.server_config.action_invocators[invocator_plugin_id]
        invocation_input: InvocationInput = invocator_plugin.populate_invocation_input(
            self.local_server.server_config,
            self.interp_ctx,
        )
        response_dict = invocation_input_desc.object_schema.dump(invocation_input)
        return response_dict

