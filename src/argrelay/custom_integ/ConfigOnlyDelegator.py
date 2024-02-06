from __future__ import annotations

import subprocess
from copy import deepcopy

from argrelay.custom_integ.ConfigOnlyDelegatorConfigSchema import config_only_delegator_config_desc, func_configs_
from argrelay.custom_integ.FuncConfigSchema import func_envelope_, command_template_
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.plugin_delegator.AbstractDelegator import AbstractDelegator, get_func_id_from_invocation_input
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InterpContext import InterpContext, function_container_ipos_
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    instance_data_,
    envelope_payload_,
)
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    search_control_list_,
    func_id_,
)
from argrelay.schema_config_interp.SearchControlSchema import (
    collection_name_,
    envelope_class_,
    keys_to_types_list_,
    populate_search_control,
)
from argrelay.schema_response.InvocationInput import InvocationInput

object_container_ipos_ = 1

class ConfigOnlyDelegator(AbstractDelegator):
    """
    Implements FS_49_96_50_77 config_only_delegator.
    """

    def __init__(
        self,
        server_config: ServerConfig,
        plugin_instance_id: str,
        plugin_config_dict: dict,
    ):
        super().__init__(
            server_config,
            plugin_instance_id,
            plugin_config_dict,
        )

    def load_config(
        self,
        plugin_config_dict,
    ) -> dict:
        """
        Populate (if missing) or assert (if present) func-related fields.
        """

        modified_plugin_config_dict = deepcopy(plugin_config_dict)
        class_to_collection_map: dict = self.server_config.class_to_collection_map

        func_configs: dict = modified_plugin_config_dict[func_configs_]
        for func_id, func_config in func_configs.items():

            func_envelope = func_config[func_envelope_]

            if ReservedArgType.EnvelopeClass.name in func_envelope:
                assert func_envelope[ReservedArgType.EnvelopeClass.name] == ReservedEnvelopeClass.ClassFunction.name
            else:
                func_envelope[ReservedArgType.EnvelopeClass.name] = ReservedEnvelopeClass.ClassFunction.name

            if ReservedArgType.FuncId.name in func_envelope:
                assert func_envelope[ReservedArgType.FuncId.name] == func_id
            else:
                func_envelope[ReservedArgType.FuncId.name] = func_id

            instance_data = func_envelope[instance_data_]

            if func_id_ in instance_data:
                assert instance_data[func_id_] == func_id
            else:
                instance_data[func_id_] = func_id

            if delegator_plugin_instance_id_ in instance_data:
                assert instance_data[delegator_plugin_instance_id_] == self.plugin_instance_id
            else:
                instance_data[delegator_plugin_instance_id_] = self.plugin_instance_id

            orig_search_control_list = func_envelope[instance_data_][search_control_list_]
            next_search_control_list = []

            for orig_search_control in orig_search_control_list:

                next_search_control = populate_search_control(
                    class_to_collection_map,
                    orig_search_control[envelope_class_],
                    orig_search_control[keys_to_types_list_],
                )

                # In general, it is allowed to have any `collection_name`, but it is likely an error
                # if configured `collection_name` is different from what `class_to_collection_map` provides:
                if collection_name_ in orig_search_control:
                    assert orig_search_control[collection_name_] == next_search_control[collection_name_]

                next_search_control_list.append(next_search_control)

            # Replace:
            func_envelope[instance_data_][search_control_list_] = next_search_control_list

            if envelope_payload_ in func_envelope:
                envelope_payload = func_envelope[envelope_payload_]
            else:
                envelope_payload = {}
                func_envelope[envelope_payload_] = envelope_payload

            if command_template_ in envelope_payload:
                assert envelope_payload[command_template_] == func_config[command_template_]
            else:
                envelope_payload[command_template_] = func_config[command_template_]

        return modified_plugin_config_dict

    def validate_config(
        self,
    ):
        config_only_delegator_config_desc.validate_dict(self.plugin_config_dict)

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:
        return [
            func_config[func_envelope_]
            for func_config in self.plugin_config_dict[func_configs_].values()
        ]

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:

        assert interp_ctx.is_func_found(), "the (first) function envelope must be found"

        # The first envelope (`DataEnvelopeSchema`) is assumed to be of
        # `ReservedEnvelopeClass.ClassFunction` with `FunctionEnvelopeInstanceDataSchema` for its `instance_data`:
        function_container = interp_ctx.envelope_containers[function_container_ipos_]
        delegator_plugin_instance_id = (
            function_container.data_envelopes[0][instance_data_]
            [delegator_plugin_instance_id_]
        )
        invocation_input = InvocationInput(
            arg_values = interp_ctx.comp_suggestions,
            all_tokens = interp_ctx.parsed_ctx.all_tokens,
            consumed_tokens = interp_ctx.consumed_tokens,
            envelope_containers = interp_ctx.envelope_containers,
            tan_token_ipos = interp_ctx.parsed_ctx.tan_token_ipos,
            tan_token_l_part = interp_ctx.parsed_ctx.tan_token_l_part,
            delegator_plugin_entry = local_server.server_config.plugin_instance_entries[
                delegator_plugin_instance_id
            ],
            custom_plugin_data = {},
        )
        return invocation_input

    @staticmethod
    def invoke_action(
        invocation_input: InvocationInput,
    ):
        # There is no way to check on client side if this function belongs to this plugin
        # (client has no access to config):
        func_id = get_func_id_from_invocation_input(invocation_input)
        func_envelope = invocation_input.envelope_containers[0].data_envelopes[0]
        func_payload = func_envelope[envelope_payload_]
        command_template: str = func_payload[command_template_]

        # Keep this as it is supposed to be referenced in the `command_template`
        object_envelope = invocation_input.envelope_containers[object_container_ipos_].data_envelopes[0]

        sub_proc = subprocess.run(
            # The input is trusted (from config), right? Then:
            # https://stackoverflow.com/a/54071505/441652
            eval(f'f""" {command_template} """'),
            shell = True,
        )
        exit(sub_proc.returncode)
