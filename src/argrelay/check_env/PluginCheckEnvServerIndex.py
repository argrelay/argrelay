from __future__ import annotations

import os.path
from typing import Union

from argrelay.check_env.CheckEnvResult import CheckEnvResult
from argrelay.check_env.PluginCheckEnvAbstract import PluginCheckEnvAbstract
from argrelay.client_command_remote.ClientCommandRemoteWorkerAbstract import (
    get_server_index_file_path,
    load_server_index,
    server_index_file_name,
)
from argrelay.enum_desc.ResultCategory import ResultCategory
from argrelay.enum_desc.TopDir import TopDir

_server_index_field_name = "server_index"


class PluginCheckEnvServerIndex(PluginCheckEnvAbstract):
    """
    This plugin reports `server_index` for FS_93_18_57_91 client fail over.
    """

    # noinspection PyMethodMayBeStatic
    def execute_check(
        self,
        online_mode: Union[bool, None],
    ) -> list[CheckEnvResult]:
        at_path = f"@/{os.path.join(TopDir.var_dir.value, server_index_file_name)}"
        if os.path.isfile(get_server_index_file_path()):

            # noinspection PyBroadException
            try:
                server_index = load_server_index()
            except:
                server_index = None

            if server_index is None:
                return [CheckEnvResult(
                    result_category = ResultCategory.VerificationFailure,
                    result_key = _server_index_field_name,
                    result_value = str(None),
                    result_message = f"Remove this file as its content cannot be read as a int: {at_path}",
                )]
            else:
                return [CheckEnvResult(
                    result_category = ResultCategory.VerificationSuccess,
                    result_key = _server_index_field_name,
                    result_value = str(server_index),
                    result_message = f"See: {at_path}",
                )]
        elif os.path.exists(get_server_index_file_path()):
            return [CheckEnvResult(
                result_category = ResultCategory.VerificationFailure,
                result_key = _server_index_field_name,
                result_value = str(None),
                result_message = f"It is not a file: {at_path}",
            )]
        else:
            if os.getenv("ARGRELAY_BOOTSTRAP_ENV") is None:
                return [CheckEnvResult(
                    result_category = ResultCategory.VerificationWarning,
                    result_key = _server_index_field_name,
                    result_value = str(None),
                    result_message = f"The client has not been used to create this file yet: {at_path}",
                )]
            else:
                return [CheckEnvResult(
                    result_category = ResultCategory.VerificationSuccess,
                    result_key = _server_index_field_name,
                    result_value = str(None),
                    result_message = f"Running with `ARGRELAY_BOOTSTRAP_ENV` - ignoring missing file: {at_path}",
                )]
