from __future__ import annotations

import re
from typing import Union

import argrelay
from argrelay.check_env.CheckEnvResult import CheckEnvResult
from argrelay.check_env.PluginCheckEnvAbstract import PluginCheckEnvAbstract
from argrelay.enum_desc.ResultCategory import ResultCategory
from argrelay.misc_helper_common import get_argrelay_dir


class PluginCheckEnvArgrelayLocalVersionMismatch(PluginCheckEnvAbstract):
    """
    Plugin reports mismatch between
    *   `argrelay.__version__`
    *   version in `@/conf/env_packages.txt`
    """

    # TODO: TODO_69_59_78_78: register known files as enum with metadata:
    file_rel_path = "conf/env_packages.txt"
    bootstrap_rel_path = "exe/bootstrap_env.bash"
    result_key = "env_packages_version"

    # noinspection PyMethodMayBeStatic
    def execute_check(
        self,
        online_mode: Union[bool, None],
    ) -> list[CheckEnvResult]:
        module_version = argrelay.__version__
        env_packages_version = self.get_env_packages_version()
        if env_packages_version is None:
            return [CheckEnvResult(
                result_category = ResultCategory.VerificationWarning,
                result_key = self.result_key,
                result_value = env_packages_version,
                result_message = f"File `@/{self.file_rel_path}` does not contain `argrelay` package => is `argrelay` installed in editable mode?",
            )]
        else:
            if env_packages_version == module_version:
                return [CheckEnvResult(
                    result_category = ResultCategory.VerificationSuccess,
                    result_key = self.result_key,
                    result_value = env_packages_version,
                    result_message = f"It matches `argrelay_module_version`",
                )]
            else:
                return [CheckEnvResult(
                    result_category = ResultCategory.VerificationFailure,
                    result_key = self.result_key,
                    result_value = env_packages_version,
                    result_message = f"It does not match `argrelay_module_version` => re-base and re-run `@/{self.bootstrap_rel_path}`",
                )]

    def get_env_packages_version(
        self,
    ):
        file_content = open(f"{get_argrelay_dir()}/{self.file_rel_path}", "rt").read()
        version_regex = r"^argrelay==(.*)$"
        regex_match = re.search(version_regex, file_content, re.M)
        if regex_match:
            return regex_match.group(1).strip()
        else:
            return None
