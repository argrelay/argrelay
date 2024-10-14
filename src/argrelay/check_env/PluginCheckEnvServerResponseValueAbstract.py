from __future__ import annotations

import traceback
from typing import cast, Union

from argrelay.check_env.CheckEnvResult import CheckEnvResult
from argrelay.check_env.PluginCheckEnvAbstract import PluginCheckEnvAbstract
from argrelay.client_command_remote.ClientCommandRemoteWorkerJson import ClientCommandRemoteWorkerJson
from argrelay.client_pipeline.BytesHandlerJson import BytesHandlerJson
from argrelay.client_pipeline.BytesSrcLocal import BytesSrcLocal
from argrelay.client_spec.ShellContext import ShellContext, UNKNOWN_COMP_KEY
from argrelay.custom_integ.SchemaPluginCheckEvnServerResponseValueAbstract import (
    field_values_to_command_lines_,
    schema_plugin_check_evn_server_response_abstract_desc,
)
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ProcRole import ProcRole
from argrelay.enum_desc.ResultCategory import ResultCategory
from argrelay.handler_response.ClientResponseHandlerCheckEnv import ClientResponseHandlerCheckEnv
from argrelay.misc_helper_common import eprint
from argrelay.relay_client.proc_worker import worker_main
from argrelay.runtime_data.ClientConfig import ClientConfig
from argrelay.schema_config_core_client.ClientConfigSchema import client_config_desc
from argrelay.schema_response.InvocationInput import InvocationInput


class PluginCheckEnvServerResponseValueAbstract(PluginCheckEnvAbstract):

    def __init__(
        self,
        plugin_instance_id: str,
        plugin_config_dict: dict,
    ):
        self.response_value_config_desc = schema_plugin_check_evn_server_response_abstract_desc
        super().__init__(
            plugin_instance_id,
            plugin_config_dict,
        )

    def validate_config(
        self,
    ) -> None:
        self.response_value_config_desc.validate_dict(self.plugin_config_dict)

    def execute_check(
        self,
        online_mode: Union[bool, None],
    ) -> list[CheckEnvResult]:

        check_env_results: list[CheckEnvResult] = []
        for field_name, command_line in self.plugin_config_dict[field_values_to_command_lines_].items():
            client_config: ClientConfig = client_config_desc.obj_from_default_file()

            for server_index in range(len(client_config.redundant_servers)):

                indexed_field_name = f"{field_name}[{server_index}]"

                # noinspection PyBroadException
                try:
                    shell_ctx = ShellContext(
                        command_line = command_line,
                        cursor_cpos = len(command_line),
                        comp_type = CompType.InvokeAction,
                        comp_key = UNKNOWN_COMP_KEY,
                        is_debug_enabled = False,
                        input_data = None,
                    )

                    call_ctx = shell_ctx.create_call_context()

                    proc_role: ProcRole = ProcRole.CheckEnvWorker

                    try:
                        command_obj: ClientCommandRemoteWorkerJson = worker_main(
                            call_ctx,
                            client_config,
                            proc_role,
                            False,
                            None,
                            server_index,
                        )
                        is_offline = False
                    except ConnectionError as e:
                        # noinspection PySimplifyBooleanCheck
                        if online_mode == True:
                            raise e
                        else:
                            is_offline = True

                    if is_offline:
                        check_env_results.append(self.verify_offline(
                            indexed_field_name,
                        ))
                    else:
                        invocation_input: InvocationInput = cast(
                            ClientResponseHandlerCheckEnv,
                            cast(
                                BytesHandlerJson,
                                cast(
                                    BytesSrcLocal,
                                    command_obj.bytes_src,
                                ).bytes_handler,
                            ).client_response_handler,
                        ).invocation_input

                        check_env_results.append(self.verify_online_value(
                            indexed_field_name,
                            invocation_input.custom_plugin_data[field_name],
                        ))

                except Exception as e:
                    eprint(traceback.format_exc())
                    check_env_results.append(CheckEnvResult(
                        result_category = ResultCategory.ExecutionFailure,
                        result_key = indexed_field_name,
                        result_value = None,
                        result_message = f"Failed: {str(type(e))}: {str(e)}",
                    ))
        return check_env_results

    def verify_online_value(
        self,
        field_name,
        field_value,
    ) -> CheckEnvResult:
        """
        Default implementation verifies nothing.
        """
        return CheckEnvResult(
            result_category = ResultCategory.VerificationSuccess,
            result_key = field_name,
            result_value = field_value,
            result_message = None,
        )

    # noinspection PyMethodMayBeStatic
    def verify_offline(
        self,
        field_name,
    ) -> CheckEnvResult:
        """
        Default implementation verifies nothing.
        """
        return CheckEnvResult(
            result_category = ResultCategory.ServerOffline,
            result_key = field_name,
            result_value = None,
            result_message = "The server is offline",
        )
