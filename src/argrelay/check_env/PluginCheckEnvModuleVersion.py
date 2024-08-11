from __future__ import annotations

from typing import Union

import argrelay
from argrelay.check_env.CheckEnvResult import CheckEnvResult
from argrelay.check_env.PluginCheckEnvAbstract import PluginCheckEnvAbstract
from argrelay.enum_desc.ResultCategory import ResultCategory


class PluginCheckEnvModuleVersion(PluginCheckEnvAbstract):
    """
    Trivial plugin to report `argrelay.__version__`.
    """

    # noinspection PyMethodMayBeStatic
    def execute_check(
        self,
        online_mode: Union[bool, None],
    ) -> list[CheckEnvResult]:
        return [CheckEnvResult(
            result_category = ResultCategory.VerificationSuccess,
            result_key = "argrelay_module_version",
            result_value = argrelay.__version__,
            result_message = None,
        )]
