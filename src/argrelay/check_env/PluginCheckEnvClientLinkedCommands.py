from __future__ import annotations

import os
import subprocess
from typing import Union

from argrelay.check_env.CheckEnvResult import CheckEnvResult
from argrelay.check_env.PluginCheckEnvAbstract import PluginCheckEnvAbstract
from argrelay.enum_desc.ResultCategory import ResultCategory
from argrelay.enum_desc.TopDir import TopDir
from argrelay.misc_helper_common import get_argrelay_dir


class PluginCheckEnvClientLinkedCommands(PluginCheckEnvAbstract):
    """
    This plugin lists values of `argrelay_bind_command_basenames` shell variable
    """

    shell_var_name: str = "argrelay_bind_command_basenames"

    # noinspection PyMethodMayBeStatic
    def execute_check(
        self,
        online_mode: Union[bool, None],
    ) -> list[CheckEnvResult]:
        conf_file_path = os.path.join(
            get_argrelay_dir(),
            TopDir.conf_dir.value,
            "shell_env.conf.bash",
        )
        shell_var_value = None
        try:
            bash_proc = subprocess.run(
                args = [
                    "bash",
                    "-c",
                    f"source {conf_file_path} ; echo ${{argrelay_bind_command_basenames[@]}}",
                ],
                capture_output = True,
            )
            assert bash_proc.returncode == 0
            stdout_str = bash_proc.stdout.decode("utf-8")
            shell_var_value = stdout_str.strip()
        except:
            shell_var_value = None

        if shell_var_value is None:
            return [CheckEnvResult(
                result_category = ResultCategory.ExecutionFailure,
                result_key = "client_linked_command",
                result_value = str(shell_var_value),
                result_message = f"unable to retrieve values of `argrelay_bind_command_basenames` from: {conf_file_path}",
            )]
        else:
            linked_commands: list[str] = shell_var_value.split()
            check_env_results: list[CheckEnvResult] = []
            for command_index, linked_command in enumerate(linked_commands):
                check_env_results.append(CheckEnvResult(
                    result_category = ResultCategory.VerificationSuccess,
                    result_key = f"client_linked_command[{command_index}]",
                    result_value = str(linked_command),
                    # result_message = f"run for more info: complete -p {linked_command}",
                    result_message = None,
                ))
            return check_env_results
