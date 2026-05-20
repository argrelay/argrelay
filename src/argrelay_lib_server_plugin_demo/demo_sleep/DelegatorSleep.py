from __future__ import annotations

import logging
import subprocess

logger = logging.getLogger()

from argrelay_api_plugin_server_abstract.delegator_utils import (
    clean_prop_value,
)
from argrelay_api_plugin_server_abstract.DelegatorAbstract import (
    get_func_id_from_interp_ctx,
    get_func_id_from_invocation_input,
)
from argrelay_api_plugin_server_abstract.DelegatorSingleFuncAbstract import (
    DelegatorSingleFuncAbstract,
)
from argrelay_api_server_cli.schema_response.InvocationInput import InvocationInput
from argrelay_app_server.relay_server.LocalServer import LocalServer
from argrelay_app_server.runtime_context.InterpContext import InterpContext
from argrelay_lib_root.enum_desc.ClientExitCode import ClientExitCode
from argrelay_lib_root.enum_desc.FuncState import FuncState
from argrelay_lib_root.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay_lib_root.enum_desc.ReservedPropName import ReservedPropName
from argrelay_lib_root.misc_helper_common import eprint
from argrelay_lib_server_plugin_core.plugin_delegator.client_invocation_utils import (
    prohibit_unconsumed_args,
)
from argrelay_schema_config_server.schema_config_interp.DataEnvelopeSchema import (
    instance_data_,
)
from argrelay_schema_config_server.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    func_id_,
    search_control_list_,
)
from argrelay_schema_config_server.schema_config_interp.SearchControlSchema import (
    populate_search_control,
)

func_id_sleep_ = "func_id_sleep"

class_sleep_ = "class_sleep"

time_delay_prop_name_ = "time_delay"

sleep_container_ipos_ = 1


class DelegatorSleep(DelegatorSingleFuncAbstract):
    """
    Demo delegator wrapping `sleep` command.

    Selects a pre-defined time delay from `class_sleep` data envelopes
    via CLI arg, strips the `s` suffix, and executes `sleep <n>`.
    """

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:

        func_envelopes = [
            {
                instance_data_: {
                    func_id_: func_id_sleep_,
                    delegator_plugin_instance_id_: self.plugin_instance_id,
                    search_control_list_: [
                        populate_search_control(
                            collection_name=class_sleep_,
                            props_to_values_dict={
                                ReservedPropName.envelope_class.name: class_sleep_,
                            },
                            arg_name_to_prop_name_map=[
                                # TODO: TODO_61_99_68_90: figure out what to do with explicit `envelope_class` `search_prop`:
                                {"class": ReservedPropName.envelope_class.name},
                                # ---
                                {"delay": time_delay_prop_name_},
                            ],
                        ),
                    ],
                },
                ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
                ReservedPropName.help_hint.name: "Use `sleep` to pause for the selected duration.",
                ReservedPropName.func_state.name: FuncState.fs_demo.name,
                ReservedPropName.func_id.name: func_id_sleep_,
            },
        ]
        return func_envelopes

    def run_invoke_control(
        self,
        interp_ctx: InterpContext,
        local_server: LocalServer,
    ) -> InvocationInput:
        assert interp_ctx.is_func_found(), "the (first) function envelope must be found"

        func_id = get_func_id_from_interp_ctx(interp_ctx)
        assert func_id == func_id_sleep_

        vararg_container = interp_ctx.envelope_containers[sleep_container_ipos_]
        vararg_container.data_envelopes = (
            local_server.get_query_engine().query_data_envelopes_for(vararg_container)
        )

        delegator_plugin_instance_id = self.plugin_instance_id
        invocation_input = InvocationInput.with_interp_context(
            interp_ctx,
            delegator_plugin_entry=local_server.plugin_config.server_plugin_instances[
                delegator_plugin_instance_id
            ],
            custom_plugin_data={},
        )
        return invocation_input

    @staticmethod
    def run_invoke_action(
        invocation_input: InvocationInput,
    ) -> int:
        func_id = get_func_id_from_invocation_input(invocation_input)
        assert func_id == func_id_sleep_

        prohibit_unconsumed_args(invocation_input)

        sleep_data_envelopes = invocation_input.envelope_containers[
            sleep_container_ipos_
        ].data_envelopes

        if len(sleep_data_envelopes) > 1:
            for sleep_data_envelope in sleep_data_envelopes:
                eprint(f"  {sleep_data_envelope}")
            eprint(
                "ERROR: `sleep` duration is ambiguous "
                "(multiple candidates based on given command line input)"
            )
            return ClientExitCode.GeneralError.value

        elif len(sleep_data_envelopes) == 0:
            eprint(
                "ERROR: `sleep` duration not found based on given command line input."
            )
            return ClientExitCode.GeneralError.value

        else:
            sleep_data_envelope = sleep_data_envelopes[0]
            return _run_sleep(sleep_data_envelope)


def _run_sleep(
    sleep_data_envelope: dict,
) -> int:
    import sys

    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
    )
    raw_delay = clean_prop_value(sleep_data_envelope[time_delay_prop_name_])
    # Strip trailing `s` suffix (e.g. "4s" → "4")
    n = int(raw_delay.rstrip("s"))
    for x in range(1, n + 1):
        logger.info(f"sleeping for a sec {x} out of {n} times...")
        sub_proc = subprocess.run(["sleep", "1"])
        if sub_proc.returncode != 0:
            return sub_proc.returncode
    return 0
