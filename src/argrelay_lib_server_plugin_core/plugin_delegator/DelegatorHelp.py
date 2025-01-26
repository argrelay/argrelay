from __future__ import annotations

from argrelay_api_plugin_server_abstract.delegator_utils import redirect_to_not_disambiguated_error
from argrelay_api_plugin_server_abstract.DelegatorAbstract import get_func_id_from_invocation_input
from argrelay_api_plugin_server_abstract.DelegatorJumpAbstract import DelegatorJumpAbstract
from argrelay_api_server_cli.schema_response.InvocationInput import InvocationInput
from argrelay_app_server.relay_server.LocalServer import LocalServer
from argrelay_app_server.runtime_context.InterpContext import (
    function_container_ipos_,
    InterpContext,
)
from argrelay_lib_root.enum_desc.FuncState import FuncState
from argrelay_lib_root.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay_lib_root.enum_desc.ReservedPropName import ReservedPropName
from argrelay_lib_root.enum_desc.SpecialFunc import SpecialFunc
from argrelay_lib_root.enum_desc.TermColor import TermColor
from argrelay_lib_server_plugin_core.plugin_delegator.client_invocation_utils import prohibit_unconsumed_args
from argrelay_lib_server_plugin_core.plugin_interp.FuncTreeInterpFactory import tree_step_prop_name_prefix_
from argrelay_schema_config_server.schema_config_interp.DataEnvelopeSchema import instance_data_
from argrelay_schema_config_server.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    func_id_,
    search_control_list_,
)
from argrelay_schema_config_server.schema_config_interp.SearchControlSchema import search_control_desc

subsequent_function_container_ipos_ = function_container_ipos_ + 1


class DelegatorHelp(DelegatorJumpAbstract):

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:
        func_envelopes = [{
            instance_data_: {
                func_id_: SpecialFunc.func_id_help_hint.name,
                delegator_plugin_instance_id_: self.plugin_instance_id,
                search_control_list_: [
                ],
            },
            ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
            ReservedPropName.help_hint.name: "List defined function matching search criteria with their help hints",
            ReservedPropName.func_state.name: FuncState.fs_gamma.name,
            ReservedPropName.func_id.name: SpecialFunc.func_id_help_hint.name,
        }]
        return func_envelopes

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:
        assert interp_ctx.is_func_found(), "the (first) function envelope must be found"

        if interp_ctx.curr_container_ipos >= subsequent_function_container_ipos_:
            subsequent_function_container = interp_ctx.envelope_containers[(
                subsequent_function_container_ipos_
            )]
            subsequent_function_container.data_envelopes = (
                local_server
                .get_query_engine()
                .query_data_envelopes_for(subsequent_function_container)
            )

            delegator_plugin_instance_id = self.plugin_instance_id

            custom_plugin_data = search_control_desc.dict_schema.dump(subsequent_function_container.search_control)

            invocation_input = InvocationInput.with_interp_context(
                interp_ctx,
                delegator_plugin_entry = local_server.plugin_config.server_plugin_instances[
                    delegator_plugin_instance_id
                ],
                custom_plugin_data = custom_plugin_data,
            )
            return invocation_input
        else:
            return redirect_to_not_disambiguated_error(
                interp_ctx,
                local_server.plugin_config,
                ReservedEnvelopeClass.class_function.name,
            )

    @staticmethod
    def invoke_action(
        invocation_input: InvocationInput,
    ) -> None:
        if get_func_id_from_invocation_input(invocation_input) == SpecialFunc.func_id_help_hint.name:

            prohibit_unconsumed_args(invocation_input)

            for data_envelope in (
                invocation_input
                    .envelope_containers[subsequent_function_container_ipos_]
                    .data_envelopes
            ):

                # Dynamic `search_control` does not contain full paths to funcs all the time -
                # it is based on curr path within FS_01_89_09_24 interp tree and FS_26_43_73_72 func tree.
                # Recognize props with the prefix instead (which are set on loading and remain static):
                tree_step_prop_names = []
                for prop_name in data_envelope:
                    if prop_name.startswith(tree_step_prop_name_prefix_):
                        tree_step_prop_names.append(prop_name)
                # Iterate through sorted prop names - `tree_step_prop_name_prefix_` is numbered:
                tree_step_prop_names.sort()
                for tree_step_prop_name in tree_step_prop_names:
                    print(f"{data_envelope[tree_step_prop_name]}", end = " ")

                # TODO: FS_02_25_41_81 (func_id_query_enum_items): perform color control only if the output is a terminal:

                print(TermColor.known_envelope_id.value, end = "")
                print("#", end = " ")
                print(TermColor.reset_style.value, end = "")

                print(TermColor.known_envelope_id.value, end = "")
                print(f"{data_envelope[instance_data_][func_id_]}", end = " ")
                print(TermColor.reset_style.value, end = "")

                print(TermColor.help_hint.value, end = "")
                print("#", end = " ")
                print(TermColor.reset_style.value, end = "")

                if ReservedPropName.help_hint.name in data_envelope:
                    print(TermColor.help_hint.value, end = "")
                    print(
                        f"{data_envelope[ReservedPropName.help_hint.name]}",
                        end = " ",
                    )
                    print(TermColor.reset_style.value, end = "")
                else:
                    print(TermColor.no_help_hint.value, end = "")
                    print(f"[no `{ReservedPropName.help_hint.name}`]", end = " ")
                    print(TermColor.reset_style.value, end = "")

                print()
