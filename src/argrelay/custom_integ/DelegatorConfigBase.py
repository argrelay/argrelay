from __future__ import annotations

from argrelay.custom_integ.FuncConfigSchema import func_envelope_, fill_control_list_
from argrelay.custom_integ.SchemaConfigDelegatorConfigBase import SchemaConfigDelegatorConfigBase
from argrelay.custom_integ.SchemaConfigDelegatorConfigOnly import func_configs_
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.misc_helper_common.TypeDesc import TypeDesc
from argrelay.plugin_delegator.DelegatorAbstract import get_func_id_from_interp_ctx
from argrelay.plugin_delegator.DelegatorSingleFuncAbstract import DelegatorSingleFuncAbstract
from argrelay.plugin_delegator.delegator_utils import set_default_to
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InterpContext import InterpContext, function_container_ipos_
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    instance_data_,
    envelope_payload_,
)
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    func_id_,
)
from argrelay.schema_response.InvocationInput import InvocationInput

object_container_ipos_ = 1


class DelegatorConfigBase(DelegatorSingleFuncAbstract):
    """
    Part of FS_49_96_50_77 config_only_delegator implementation.
    """

    def __init__(
        self,
        server_config: ServerConfig,
        plugin_instance_id: str,
        plugin_config_dict: dict,
        delegator_config_desc: TypeDesc,
    ):
        assert issubclass(delegator_config_desc.dict_schema.__class__, SchemaConfigDelegatorConfigBase)
        self.delegator_config_desc = delegator_config_desc

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

        modified_plugin_config_dict = self.delegator_config_desc.dict_from_input_dict(plugin_config_dict)

        func_configs: dict = modified_plugin_config_dict[func_configs_]
        for func_id, func_config in func_configs.items():

            func_envelope = func_config[func_envelope_]

            if ReservedPropName.envelope_class.name in func_envelope:
                assert func_envelope[ReservedPropName.envelope_class.name] == ReservedEnvelopeClass.class_function.name
            else:
                func_envelope[ReservedPropName.envelope_class.name] = ReservedEnvelopeClass.class_function.name

            if ReservedPropName.func_id.name in func_envelope:
                assert func_envelope[ReservedPropName.func_id.name] == func_id
            else:
                func_envelope[ReservedPropName.func_id.name] = func_id

            instance_data = func_envelope[instance_data_]

            if func_id_ in instance_data:
                assert instance_data[func_id_] == func_id
            else:
                instance_data[func_id_] = func_id

            if delegator_plugin_instance_id_ in instance_data:
                assert instance_data[delegator_plugin_instance_id_] == self.plugin_instance_id
            else:
                instance_data[delegator_plugin_instance_id_] = self.plugin_instance_id

            if envelope_payload_ in func_envelope:
                envelope_payload = func_envelope[envelope_payload_]
            else:
                envelope_payload = {}
                func_envelope[envelope_payload_] = envelope_payload

        return modified_plugin_config_dict

    def validate_config(
        self,
    ) -> None:
        # Re-validate schema because `load_config` applies changes to config:
        self.delegator_config_desc.validate_dict(self.plugin_config_dict)

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:
        return [
            func_config[func_envelope_]
            for func_config in self.plugin_config_dict[func_configs_].values()
        ]

    def has_fill_control(
        self,
    ) -> bool:
        return True

    def run_fill_control(
        self,
        interp_ctx: InterpContext,
    ) -> bool:
        """
        FS_49_96_50_77: (part of implementation for config-only delegator) populates defaults

        TODO: TODO_54_68_18_12: Support defaults for config-only delegator
        """
        any_assignment = False
        if interp_ctx.curr_container_ipos > function_container_ipos_:
            func_id = get_func_id_from_interp_ctx(interp_ctx)
            func_config = self.plugin_config_dict[func_configs_][func_id]
            if fill_control_list_ in func_config:
                fill_control_list = func_config[fill_control_list_]
                if interp_ctx.curr_container_ipos < len(fill_control_list):

                    # Define vars in current context to evaluate `prop_value_template` below:
                    envelope_containers = interp_ctx.envelope_containers

                    fill_control: dict = fill_control_list[interp_ctx.curr_container_ipos]
                    for prop_name, prop_value_template in fill_control.items():
                        if prop_value_template is not None:
                            # The input is trusted (from config), right? Then:
                            # https://stackoverflow.com/a/54071505/441652
                            prop_value = eval(f'f"""{prop_value_template}"""')

                            any_assignment = (
                                set_default_to(prop_name, prop_value, interp_ctx.curr_container)
                                or
                                any_assignment
                            )

        return any_assignment

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:

        assert interp_ctx.is_func_found(), "the (first) function envelope must be found"

        # The first envelope (`DataEnvelopeSchema`) is assumed to be of
        # `ReservedEnvelopeClass.class_function` with `FunctionEnvelopeInstanceDataSchema` for its `instance_data`:
        function_container = interp_ctx.envelope_containers[function_container_ipos_]
        delegator_plugin_instance_id = (
            function_container.data_envelopes[0][instance_data_]
            [delegator_plugin_instance_id_]
        )
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
        raise NotImplementedError("Extend: not implemented intentionally")
