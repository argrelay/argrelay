from __future__ import annotations

from argrelay.custom_integ.ServiceDelegator import redirect_to_no_func_error
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.SpecialFunc import SpecialFunc
from argrelay.enum_desc.TermColor import TermColor
from argrelay.plugin_delegator.AbstractDelegator import get_data_envelopes
from argrelay.plugin_delegator.InterceptDelegator import InterceptDelegator
from argrelay.plugin_delegator.InvocationInput import InvocationInput
from argrelay.plugin_interp.AbstractInterp import AbstractInterp
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.relay_server.QueryEngine import populate_query_dict
from argrelay.runtime_context.InterpContext import function_envelope_ipos_, InterpContext
from argrelay.runtime_context.SearchControl import SearchControl
from argrelay.schema_config_interp.DataEnvelopeSchema import envelope_id_
from argrelay.schema_config_interp.SearchControlSchema import search_control_desc

subsequent_function_envelope_ipos_ = function_envelope_ipos_ + 1


# TODO: It inherits `InterceptDelegator`, but it makes more sense to have common base class instead.
class HelpDelegator(InterceptDelegator):

    def run_interp_control(
        self,
        curr_interp: AbstractInterp,
    ) -> str:
        # TODO: This must be special interpreter which is configured only to search functions (without their args).
        return super().run_interp_control(curr_interp)

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:
        assert interp_ctx.is_funct_found(), "the (first) function envelope must be found"

        if interp_ctx.curr_container_ipos >= subsequent_function_envelope_ipos_:
            subsequent_function_container = interp_ctx.envelope_containers[(
                subsequent_function_envelope_ipos_
            )]
            query_dict = populate_query_dict(subsequent_function_container)
            delegator_plugin_instance_id = HelpDelegator.__name__

            custom_plugin_data = search_control_desc.dict_schema.dump(subsequent_function_container.search_control)

            invocation_input = InvocationInput(
                all_tokens = interp_ctx.parsed_ctx.all_tokens,
                consumed_tokens = interp_ctx.consumed_tokens,
                delegator_plugin_entry = local_server.server_config.plugin_dict[delegator_plugin_instance_id],
                data_envelopes = (
                    # Envelope of `SpecialFunc.help_func`:
                    get_data_envelopes(interp_ctx)[:subsequent_function_envelope_ipos_]
                    +
                    # These must be function envelopes found via query:
                    local_server.get_query_engine().query_data_envelopes(query_dict)
                ),
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
        search_control: SearchControl = search_control_desc.dict_schema.load(invocation_input.custom_plugin_data)
        if invocation_input.data_envelopes[function_envelope_ipos_][envelope_id_] == SpecialFunc.help_func.name:
            for data_envelope in invocation_input.data_envelopes[subsequent_function_envelope_ipos_:]:

                # Print fields from search control:
                for keys_to_types in search_control.keys_to_types_list:
                    # There should be only one (key, value) pair:
                    key_name = next(iter(keys_to_types))
                    type_name = keys_to_types[key_name]
                    print(f"{data_envelope[type_name]}", end = " ")

                # TODO: perform color control only if the output is a terminal:

                print(TermColor.BRIGHT_BLACK.value, end = "")
                print("#", end = " ")
                print(TermColor.RESET.value, end = "")

                if envelope_id_ in data_envelope:
                    print(TermColor.BRIGHT_BLACK.value, end = "")
                    print(f"{data_envelope[envelope_id_]}", end = " ")
                    print(TermColor.RESET.value, end = "")
                else:
                    print(TermColor.DARK_RED.value, end = "")
                    print(f"[no `{envelope_id_}`]", end = " ")
                    print(TermColor.RESET.value, end = "")

                print(TermColor.DARK_GREEN.value, end = "")
                print("#", end = " ")
                print(TermColor.RESET.value, end = "")

                if ReservedArgType.HelpHint.name in data_envelope:
                    print(TermColor.DARK_GREEN.value, end = "")
                    print(
                        f"{data_envelope[ReservedArgType.HelpHint.name]}",
                        end = " ",
                    )
                    print(TermColor.RESET.value, end = "")
                else:
                    print(TermColor.DARK_RED.value, end = "")
                    print(f"[no `{ReservedArgType.HelpHint.name}`]", end = " ")
                    print(TermColor.RESET.value, end = "")

                print()
