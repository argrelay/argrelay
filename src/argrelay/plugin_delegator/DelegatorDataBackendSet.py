from __future__ import annotations

import dataclasses
import sys

from argrelay.enum_desc.FuncState import FuncState
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.enum_desc.SpecialFunc import SpecialFunc
from argrelay.misc_helper_common import eprint
from argrelay.mongo_data.ProgressTracker import ProgressTracker
from argrelay.plugin_delegator.DelegatorAbstract import get_func_id_from_invocation_input, get_func_id_from_interp_ctx
from argrelay.plugin_delegator.DelegatorDataBackendBase import get_collection_search_control, DelegatorDataBackendBase
from argrelay.plugin_delegator.delegator_utils import redirect_to_not_disambiguated_error
from argrelay.plugin_loader.client_invocation_utils import prohibit_unconsumed_args
from argrelay.relay_client.__main__ import run_client
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.relay_server.QueryEngine import populate_query_dict
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.runtime_data.ClientConfig import ClientConfig
from argrelay.runtime_data.EnvelopeCollection import EnvelopeCollection
from argrelay.schema_config_core_client.ClientConfigSchema import client_config_desc
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    instance_data_,
    data_envelope_desc,
)
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    search_control_list_,
    func_id_,
)
from argrelay.schema_response.InvocationInput import InvocationInput

collection_name_container_ipos_ = 1
data_envelope_container_ipos_ = 2


class DelegatorDataBackendSet(DelegatorDataBackendBase):
    """
    Implements `SpecialFunc.func_id_set_data_envelopes` for FS_74_69_61_79 get set data envelope.
    """

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:

        collection_search_control = get_collection_search_control(
        )

        func_envelopes = []

        given_function_envelope = {
            instance_data_: {
                func_id_: SpecialFunc.func_id_set_data_envelopes.name,
                delegator_plugin_instance_id_: self.plugin_instance_id,
                search_control_list_: [
                    collection_search_control,
                ],
            },
            ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
            ReservedPropName.help_hint.name: "Set `data_envelope`-s based on their `index_prop`-s.",
            ReservedPropName.func_state.name: FuncState.fs_alpha.name,
            ReservedPropName.func_id.name: SpecialFunc.func_id_set_data_envelopes.name,
        }
        func_envelopes.append(given_function_envelope)

        return func_envelopes

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:

        assert interp_ctx.is_func_found(), "the (first) function envelope must be found"

        func_id = get_func_id_from_interp_ctx(interp_ctx)
        assert func_id == SpecialFunc.func_id_set_data_envelopes.name

        vararg_container_ipos = data_envelope_container_ipos_

        # Verify that func is selected:
        if interp_ctx.curr_container_ipos < vararg_container_ipos:
            return redirect_to_not_disambiguated_error(
                interp_ctx,
                local_server.plugin_config,
                ReservedEnvelopeClass.class_collection.name,
            )

        collection_container = interp_ctx.envelope_containers[collection_name_container_ipos_]
        vararg_container = interp_ctx.envelope_containers[vararg_container_ipos]

        # FS_74_69_61_79 get set data envelope:
        # The way `get` is implemented via double `ServerAction.RelayLineArgs` call:
        # *   The first request to the server without `input_data` sends invocation data to the client.
        # *   The client runs the second request with `input_data` collected (e.g. from `stdin`).

        if interp_ctx.parsed_ctx.input_data is None:
            # 1st request
            pass

        else:
            # 2nd request

            # All what is left to do is to delete and store objects.

            # Delete:
            collection_name = collection_container.assigned_prop_name_to_prop_value[
                ReservedPropName.collection_name.name
            ].prop_value
            query_dict = populate_query_dict(vararg_container)
            eprint(f"delete: {query_dict}")
            local_server.delete_data_envelopes(
                collection_name,
                query_dict,
            )

            # Store:
            data_envelopes = []
            for json_line in interp_ctx.parsed_ctx.input_data.splitlines():
                if len(json_line.strip()) == 0:
                    continue
                data_envelopes.append(data_envelope_desc.obj_from_yaml_str(json_line))
            envelope_collection = EnvelopeCollection(
                collection_name = collection_name,
                data_envelopes = data_envelopes,
            )
            eprint(f"envelope_collection: {envelope_collection}")
            progress_tracker = ProgressTracker()
            local_server.store_mongo_data_step(
                [envelope_collection],
                "",
                progress_tracker,
            )

            # Post-validate:
            local_server.post_validate_collection_for_missing_index_prop_names(
                collection_name,
                progress_tracker,
            )

            # Invalidate cache:
            local_server.invalidate_cache_for_collection(collection_name)

        # Plugin to invoke on client side:
        delegator_plugin_instance_id = self.plugin_instance_id
        # Package into `InvocationInput` payload object:
        invocation_input = InvocationInput.with_interp_context(
            interp_ctx,
            delegator_plugin_entry = local_server.plugin_config.server_plugin_instances[
                delegator_plugin_instance_id
            ],
            custom_plugin_data = {},
        )
        return invocation_input

    @staticmethod
    def invoke_action(
        invocation_input: InvocationInput,
    ) -> None:
        func_id = get_func_id_from_invocation_input(invocation_input)
        assert func_id == SpecialFunc.func_id_set_data_envelopes.name

        prohibit_unconsumed_args(invocation_input)

        if invocation_input.call_ctx.input_data is None:
            # 1st response

            call_ctx = dataclasses.replace(
                invocation_input.call_ctx,
                # FS_74_69_61_79 get set data envelope:
                # Load data from stdin and call REST API to update data on the server:
                input_data = sys.stdin.read(),
            )

            if sys.stdin.isatty():
                eprint("provide `data_envelope` one JSON per line:")

            client_config: ClientConfig = client_config_desc.obj_from_default_file()
            if len(client_config.redundant_servers) > 1:
                eprint("WARN: this command may only update data for one of the `redundant_servers` in `client_config`")

            run_client(
                client_config,
                call_ctx,
            )
        else:
            # 2nd response
            pass
