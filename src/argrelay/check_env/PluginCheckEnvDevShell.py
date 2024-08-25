from __future__ import annotations

import os
import time
from datetime import datetime
from typing import Union

from argrelay.check_env.CheckEnvResult import CheckEnvResult
from argrelay.check_env.PluginCheckEnvAbstract import PluginCheckEnvAbstract
from argrelay.check_env.check_env_utils import format_time_to_relative
from argrelay.enum_desc.ResultCategory import ResultCategory


class PluginCheckEnvDevShell(PluginCheckEnvAbstract):
    """
    This plugin reports value of `ARGRELAY_DEV_SHELL` env var.
    """

    env_var_name: str = "ARGRELAY_DEV_SHELL"

    # noinspection PyMethodMayBeStatic
    def execute_check(
        self,
        online_mode: Union[bool, None],
    ) -> list[CheckEnvResult]:
        env_var_value = os.environ.get(self.env_var_name)

        if env_var_value is None:
            result_message = "The env var is not set => outside `@/exe/dev_shell.bash`."
        else:
            curr_time_ms = time.time() * 1000
            prev_time_ms = convert_iso_str_date_to_ms(env_var_value)
            if prev_time_ms is None:
                result_message = f"The env var is set => inside `@/exe/dev_shell.bash`."
            else:
                rel_time: str = format_time_to_relative(
                    curr_time_ms,
                    prev_time_ms,
                )
                result_message = f"~ {rel_time}: the env var is set => inside `@/exe/dev_shell.bash`."

        return [CheckEnvResult(
            result_category = ResultCategory.VerificationSuccess,
            result_key = self.env_var_name,
            result_value = str(env_var_value),
            result_message = result_message,
        )]


def convert_iso_str_date_to_ms(
    date_str: str,
) -> Union[int, None]:
    try:
        return int(datetime.fromisoformat(date_str).timestamp()) * 1000
    except:
        return None
