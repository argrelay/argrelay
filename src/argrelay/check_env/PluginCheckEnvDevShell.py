from __future__ import annotations

import os
from typing import Union

from argrelay.check_env.CheckEnvResult import CheckEnvResult
from argrelay.check_env.PluginCheckEnvAbstract import PluginCheckEnvAbstract
from argrelay.enum_desc.ResultCategory import ResultCategory


class PluginCheckEnvDevShell(PluginCheckEnvAbstract):
    """
    Trivial plugin to report value of `ARGRELAY_DEV_SHELL` env var.
    """

    env_var_name: str = "ARGRELAY_DEV_SHELL"

    # noinspection PyMethodMayBeStatic
    def execute_check(
        self,
        online_mode: Union[bool, None],
    ) -> list[CheckEnvResult]:
        env_var_value = os.environ.get(self.env_var_name)
        if env_var_value is None:
            result_message = "env var is not set => outside `@/exe/dev_shell.bash`"
        else:
            result_message = "env var is set => inside `@/exe/dev_shell.bash`"
        return [CheckEnvResult(
            result_category = ResultCategory.VerificationSuccess,
            result_key = self.env_var_name,
            result_value = str(env_var_value),
            result_message = result_message,
        )]
