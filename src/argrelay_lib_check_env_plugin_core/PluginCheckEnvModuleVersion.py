from __future__ import annotations

from typing import Union

import argrelay
from argrelay_api_plugin_check_env_abstract.CheckEnvResult import CheckEnvResult
from argrelay_api_plugin_check_env_abstract.PluginCheckEnvAbstract import PluginCheckEnvAbstract
from argrelay_lib_root.enum_desc.ResultCategory import ResultCategory


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
