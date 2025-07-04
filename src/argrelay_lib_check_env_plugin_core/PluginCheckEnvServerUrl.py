from __future__ import annotations

from typing import Union

from argrelay_api_plugin_check_env_abstract.CheckEnvResult import CheckEnvResult
from argrelay_api_plugin_check_env_abstract.PluginCheckEnvAbstract import (
    PluginCheckEnvAbstract,
)
from argrelay_lib_root.enum_desc.ResultCategory import ResultCategory
from argrelay_schema_config_client.runtime_data_client_app.ClientConfig import (
    ClientConfig,
)
from argrelay_schema_config_client.schema_config_client_app.ClientConfigSchema import (
    client_config_desc,
)


class PluginCheckEnvServerUrl(PluginCheckEnvAbstract):
    """
    Simple plugin which lists URL-s for configured servers.
    """

    # noinspection PyMethodMayBeStatic
    def execute_check(
        self,
        online_mode: Union[bool, None],
    ) -> list[CheckEnvResult]:
        check_env_results: list[CheckEnvResult] = []
        client_config: ClientConfig = client_config_desc.obj_from_default_file()
        for server_index, redundant_server in enumerate(
            client_config.redundant_servers
        ):
            check_env_results.append(
                CheckEnvResult(
                    result_category=ResultCategory.VerificationSuccess,
                    result_key=f"server_url[{server_index}]",
                    result_value=f"http://{redundant_server.server_host_name}:{redundant_server.server_port_number}",
                    result_message=None,
                )
            )
        return check_env_results
