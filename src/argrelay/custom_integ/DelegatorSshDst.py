from __future__ import annotations

import json
import os
import subprocess

from argrelay.custom_integ.ServicePropName import ServicePropName
from argrelay.enum_desc.ClientExitCode import ClientExitCode
from argrelay.enum_desc.FuncState import FuncState
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.misc_helper_common import eprint
from argrelay.plugin_delegator.DelegatorAbstract import (
    get_func_id_from_interp_ctx,
    get_func_id_from_invocation_input,
)
from argrelay.plugin_delegator.DelegatorSingleFuncAbstract import DelegatorSingleFuncAbstract
from argrelay.plugin_delegator.delegator_utils import (
    clean_prop_value,
)
from argrelay.plugin_loader.client_invocation_utils import prohibit_unconsumed_args
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.runtime_context.InterpContext import InterpContext
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    instance_data_,
)
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
    search_control_list_,
    func_id_,
)
from argrelay.schema_config_interp.SearchControlSchema import populate_search_control
from argrelay.schema_response.InvocationInput import InvocationInput

func_id_ssh_dst_ = "func_id_ssh_dst"

class_ssh_dst_ = "class_ssh_dst"

ssh_dst_container_ipos_ = 1


class DelegatorSshDst(DelegatorSingleFuncAbstract):
    """
    This is a demo delegator wrapping `ssh` command.

    Unlike naked `ssh`, wrapped `ssh` allows selecting destinations by
    user-specific metadata properties - see `search_control_list_`.

    It reuses metadata properties defined in `ServicePropName` simply to
    avoid re-defining something similar for demo purposes, but it is a standalone
    plugin otherwise.

    It is possible to categorize `ssh` destination by any of `ServicePropName`-s.
    """

    def get_supported_func_envelopes(
        self,
    ) -> list[dict]:

        func_envelopes = [
            {
                instance_data_: {
                    func_id_: func_id_ssh_dst_,
                    delegator_plugin_instance_id_: self.plugin_instance_id,
                    search_control_list_: [
                        populate_search_control(
                            collection_name = class_ssh_dst_,
                            props_to_values_dict = {
                                ReservedPropName.envelope_class.name: class_ssh_dst_,
                            },
                            arg_name_to_prop_name_map = [
                                # TODO: TODO_61_99_68_90: figure out what to do with explicit `envelope_class` `search_prop`:
                                {"class": ReservedPropName.envelope_class.name},
                                # ---
                                {"code": ServicePropName.code_maturity.name},
                                {"stage": ServicePropName.flow_stage.name},
                                {"region": ServicePropName.geo_region.name},
                                {"cluster": ServicePropName.cluster_name.name},
                                # ---
                                {"group": ServicePropName.group_label.name},
                                {"service": ServicePropName.service_name.name},
                                {"mode": ServicePropName.run_mode.name},
                                # ---
                                {"user": ServicePropName.user_name.name},
                                {"host": ServicePropName.host_name.name},
                                {"path": ServicePropName.dir_path.name},
                                # ---
                                {"status": ServicePropName.live_status.name},
                                {"dc": ServicePropName.data_center.name},
                                {"ip": ServicePropName.ip_address.name},
                            ],
                        ),
                    ],
                },
                ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
                ReservedPropName.help_hint.name: "Use `ssh` to log into the destination.",
                ReservedPropName.func_state.name: FuncState.fs_demo.name,
                ReservedPropName.func_id.name: func_id_ssh_dst_,
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
        assert func_id == func_id_ssh_dst_

        # Even if these functions do not support varargs, query all - let client decide what to do.
        # Search `data_envelope`-s based on existing args on command line:
        vararg_container = interp_ctx.envelope_containers[ssh_dst_container_ipos_]
        vararg_container.data_envelopes = (
            local_server
            .get_query_engine()
            .query_data_envelopes_for(vararg_container)
        )

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
        assert func_id == func_id_ssh_dst_

        prohibit_unconsumed_args(invocation_input)

        ssh_dst_data_envelopes = invocation_input.envelope_containers[ssh_dst_container_ipos_].data_envelopes

        if len(ssh_dst_data_envelopes) > 1:
            for ssh_dst_data_envelope in ssh_dst_data_envelopes:
                eprint(_data_envelope_to_str(ssh_dst_data_envelope))

            # TODO: TODO_20_61_16_31 `cardinality_hook`: run different funcs based on `data_envelope` set size
            eprint(
                "ERROR: `ssh` destination is ambiguous "
                "(multiple candidates based on given command line input)"
            )
            exit(ClientExitCode.GeneralError.value)

        elif len(ssh_dst_data_envelopes) == 0:
            eprint("ERROR: `ssh` destination not found based on given command line input.")
            exit(ClientExitCode.GeneralError.value)

        else:
            ssh_dst_data_envelope = ssh_dst_data_envelopes[0]
            _run_ssh(ssh_dst_data_envelope)


def _data_envelope_to_str(
    data_envelope: dict,
) -> str:
    return json.dumps(
        data_envelope,
        indent = 4,
    )


def _run_ssh(
    ssh_dst_data_envelope: dict,
) -> None:
    eprint(_data_envelope_to_str(ssh_dst_data_envelope))

    user_name = clean_prop_value(ssh_dst_data_envelope[ServicePropName.user_name.name])
    if not user_name:
        user_name = os.getlogin()

    host_name = clean_prop_value(ssh_dst_data_envelope[ServicePropName.host_name.name])
    dir_path = clean_prop_value(ssh_dst_data_envelope[ServicePropName.dir_path.name])

    ssh_dst = f"{user_name}@{host_name}:{dir_path}"
    eprint(f"INFO: starting shell via `ssh` at destination: {ssh_dst}")

    # Run `ssh` by starting shell explicitly to select required target dir:
    sub_proc = subprocess.run(
        [
            "ssh",
            "-t",
            f"{user_name}@{host_name}",
            f"cd \"{dir_path}\" ; bash --login",
        ],
    )
    exit_code = sub_proc.returncode
    exit(exit_code)
