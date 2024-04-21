from __future__ import annotations

from argrelay.custom_integ.ServiceDelegator import redirect_to_no_func_error
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.SpecialFunc import SpecialFunc
from argrelay.enum_desc.TermColor import TermColor
from argrelay.plugin_delegator.AbstractDelegator import get_func_id_from_invocation_input
from argrelay.plugin_delegator.AbstractJumpDelegator import AbstractJumpDelegator
from argrelay.plugin_interp.FuncTreeInterpFactory import tree_path_selector_prefix_
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InterpContext import function_container_ipos_, InterpContext
from argrelay.schema_config_interp.DataEnvelopeSchema import instance_data_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    search_control_list_,
    func_id_,
)
from argrelay.schema_config_interp.SearchControlSchema import search_control_desc
from argrelay.schema_response.InvocationInput import InvocationInput

subsequent_function_container_ipos_ = function_container_ipos_ + 1


class HelpDelegator(AbstractJumpDelegator):

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:
        func_envelopes = [{
            instance_data_: {
                func_id_: SpecialFunc.help_hint_func.name,
                delegator_plugin_instance_id_: self.plugin_instance_id,
                search_control_list_: [
                ],
            },
            ReservedArgType.EnvelopeClass.name: ReservedEnvelopeClass.ClassFunction.name,
            ReservedArgType.HelpHint.name: "List defined function matching search criteria with their help hints",
            ReservedArgType.FuncId.name: SpecialFunc.help_hint_func.name,
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
                delegator_plugin_entry = local_server.server_config.plugin_instance_entries[
                    delegator_plugin_instance_id
                ],
                custom_plugin_data = custom_plugin_data,
            )
            return invocation_input
        else:
            return redirect_to_no_func_error(
                interp_ctx,
                local_server.server_config,
            )

    @staticmethod
    def invoke_action(invocation_input: InvocationInput):
        if get_func_id_from_invocation_input(invocation_input) == SpecialFunc.help_hint_func.name:
            for data_envelope in (
                invocation_input
                    .envelope_containers[subsequent_function_container_ipos_]
                    .data_envelopes
            ):

                # Dynamic `search_control` does not contain full paths to funcs all the time -
                # it is based on curr path within FS_01_89_09_24 interp tree and FS_26_43_73_72 func tree.
                # Recognize props with the prefix instead (which are set on loading and remain static):
                tree_path_selector_prop_names = []
                for prop_name in data_envelope:
                    if prop_name.startswith(tree_path_selector_prefix_):
                        tree_path_selector_prop_names.append(prop_name)
                # Iterate through sorted prop names - `tree_path_selector_prefix_` is numbered:
                tree_path_selector_prop_names.sort()
                for tree_path_selector_prop_name in tree_path_selector_prop_names:
                    print(f"{data_envelope[tree_path_selector_prop_name]}", end = " ")

                # TODO: FS_02_25_41_81 (query_enum_items_func): perform color control only if the output is a terminal:

                print(TermColor.known_envelope_id.value, end = "")
                print("#", end = " ")
                print(TermColor.reset_style.value, end = "")

                print(TermColor.known_envelope_id.value, end = "")
                print(f"{data_envelope[instance_data_][func_id_]}", end = " ")
                print(TermColor.reset_style.value, end = "")

                print(TermColor.help_hint.value, end = "")
                print("#", end = " ")
                print(TermColor.reset_style.value, end = "")

                if ReservedArgType.HelpHint.name in data_envelope:
                    print(TermColor.help_hint.value, end = "")
                    print(
                        f"{data_envelope[ReservedArgType.HelpHint.name]}",
                        end = " ",
                    )
                    print(TermColor.reset_style.value, end = "")
                else:
                    print(TermColor.no_help_hint.value, end = "")
                    print(f"[no `{ReservedArgType.HelpHint.name}`]", end = " ")
                    print(TermColor.reset_style.value, end = "")

                print()
