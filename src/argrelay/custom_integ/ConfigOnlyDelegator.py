from __future__ import annotations

import subprocess

from argrelay.custom_integ.BaseConfigDelegator import BaseConfigDelegator
from argrelay.custom_integ.ConfigOnlyDelegatorConfigSchema import (
    config_only_delegator_config_desc,
    command_template_,
    echo_command_on_stderr_,
)
from argrelay.misc_helper_common import eprint
from argrelay.plugin_delegator.AbstractDelegator import get_func_id_from_invocation_input
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.schema_config_interp.DataEnvelopeSchema import (
    envelope_payload_,
)
from argrelay.schema_response.InvocationInput import InvocationInput

object_container_ipos_ = 1


class ConfigOnlyDelegator(BaseConfigDelegator):
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
            config_only_delegator_config_desc,
        )

    @staticmethod
    def invoke_action(
        invocation_input: InvocationInput,
    ):
        # TODO_74_73_60_93: Support expected envelope count in config-only delegator:
        # Use common static functions in `BaseConfigDelegator`.

        # Keep this as it is supposed to be referenced in the `command_template`
        envelope_containers = invocation_input.envelope_containers

        # There is no way to check on client side if this function belongs to this plugin
        # (client has no access to config):
        func_id = get_func_id_from_invocation_input(invocation_input)
        func_envelope = invocation_input.envelope_containers[0].data_envelopes[0]
        func_payload = func_envelope[envelope_payload_]
        command_template: str = func_payload[command_template_]

        # The input is trusted (from config), right? Then:
        # https://stackoverflow.com/a/54071505/441652
        command_line = eval(f'f"""\n{command_template}\n"""')

        if func_payload[echo_command_on_stderr_]:
            eprint(f"INFO: command_line:\n{command_line}")

        sub_proc = subprocess.run(
            command_line,
            shell = True,
        )
        exit(sub_proc.returncode)
