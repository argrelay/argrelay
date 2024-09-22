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
    This plugin checks which `argrelay_dir` each command is linked to.

    This is related to FS_57_36_37_48 multiple clients coexistence.

    It loops through values keys of `argrelay_basename_to_client_path_map` shell variable
    (which is supposed to map each linked command to a client with potentially different `argrelay_dir`).
    Then, it verifies `argrelay_dir` of the mapped client with the `argrelay_dir` of currently running process.
    """

    # noinspection PyMethodMayBeStatic
    def execute_check(
        self,
        online_mode: Union[bool, None],
    ) -> list[CheckEnvResult]:
        dev_shell_path = os.path.join(
            get_argrelay_dir(),
            TopDir.exe_dir.value,
            "dev_shell.bash",
        )
        shell_var_value = None
        try:
            bash_proc = subprocess.run(
                args = [
                    dev_shell_path,
                    f"echo ${{!argrelay_basename_to_client_path_map[@]}}",
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
                result_message = f"Unable to retrieve keys of `argrelay_basename_to_client_path_map` under started: {dev_shell_path}",
            )]
        else:
            linked_commands: list[str] = shell_var_value.split()
            check_env_results: list[CheckEnvResult] = []
            for command_index, linked_command in enumerate(linked_commands):

                shell_var_value = None
                try:
                    bash_proc = subprocess.run(
                        args = [
                            dev_shell_path,
                            f"echo ${{argrelay_basename_to_client_path_map[{linked_command}]}}",
                        ],
                        capture_output = True,
                    )
                    assert bash_proc.returncode == 0
                    stdout_str = bash_proc.stdout.decode("utf-8")
                    shell_var_value = stdout_str.strip()
                except:
                    shell_var_value = None

                if shell_var_value is None:
                    check_env_results.append(CheckEnvResult(
                        result_category = ResultCategory.ExecutionFailure,
                        result_key = f"client_linked_command[{command_index}]",
                        result_value = str(linked_command),
                        result_message = f"Unable to map `{linked_command}` to `@/exe/run_argrelay_client`",
                    ))
                else:
                    argrelay_client_path = shell_var_value
                    if argrelay_client_path == f"{get_argrelay_dir()}/exe/run_argrelay_client":
                        check_env_results.append(CheckEnvResult(
                            result_category = ResultCategory.VerificationSuccess,
                            result_key = f"client_linked_command[{command_index}]",
                            result_value = str(linked_command),
                            result_message = "Command is linked to `@/exe/run_argrelay_client` from this `argrelay_dir`",
                        ))
                    else:
                        check_env_results.append(CheckEnvResult(
                            result_category = ResultCategory.VerificationWarning,
                            result_key = f"client_linked_command[{command_index}]",
                            result_value = str(linked_command),
                            result_message = f"Command is linked to another `argrelay_dir` with: {argrelay_client_path}",
                        ))

            return check_env_results
