from __future__ import annotations

from typing import Union

from argrelay.check_env.CheckEnvResult import CheckEnvResult
from argrelay.check_env.PluginCheckEnvAbstract import PluginCheckEnvAbstract
from argrelay.enum_desc.ResultCategory import ResultCategory


class PluginCheckEnvOnlineMode(PluginCheckEnvAbstract):
    """
    Trivial plugin to report value of `online_mode`.
    """

    # noinspection PyMethodMayBeStatic
    def execute_check(
        self,
        online_mode: Union[bool, None],
    ) -> list[CheckEnvResult]:
        if online_mode is None:
            result_message = "Use `offline` or `online` arg to force specific mode."
        elif online_mode:
            result_message = "Enforced `online` mode to report errors on server connection failure."
        else:
            result_message = "Enforced `offline` mode to avoid connection to server."
        return [CheckEnvResult(
            result_category = ResultCategory.VerificationSuccess,
            result_key = "online_mode",
            result_value = str(online_mode),
            result_message = result_message,
        )]
