from __future__ import annotations

import os.path
from typing import Union

from argrelay.check_env.CheckEnvResult import CheckEnvResult
from argrelay.check_env.PluginCheckEnvAbstract import PluginCheckEnvAbstract
from argrelay.custom_integ.git_utils import is_git_repo, get_unversioned_file_list
from argrelay.enum_desc.ResultCategory import ResultCategory
from argrelay.misc_helper_common import get_argrelay_dir


class PluginCheckEnvArgrelayUnversionedSymlinks(PluginCheckEnvAbstract):
    """
    Plugin reports unversioned and unignored symlinks.

    Some common files are normally installed as symlinks rather than a copy.

    It is likely that those unversioned and unignored symlinks are leftover of upgrades
    (via `@/exe/bootstrap_env.bash`) from one version to another because
    such upgrade procedures are NOT complicated by tracking what was in
    multitude of old versions to be changed on upgrade to multiple of new versions.
    """

    field_name = "unversioned_symlink"

    # noinspection PyMethodMayBeStatic
    def execute_check(
        self,
        online_mode: Union[bool, None],
    ) -> list[CheckEnvResult]:
        argrelay_dir = get_argrelay_dir()

        if is_git_repo(argrelay_dir):
            try:
                unversioned_file_list: list[str] = get_unversioned_file_list(argrelay_dir)
            except ValueError:
                unversioned_file_list = None
        else:
            unversioned_file_list = None

        if unversioned_file_list is None:
            return [CheckEnvResult(
                result_category = ResultCategory.ExecutionFailure,
                result_key = self.field_name,
                result_value = None,
                result_message = "Failed to retrieve unversioned files from git repo.",
            )]
        else:
            results_per_file: list[CheckEnvResult] = []
            for unversioned_file in unversioned_file_list:
                full_path = os.path.join(argrelay_dir, unversioned_file)
                if os.path.islink(full_path):
                    results_per_file.append(CheckEnvResult(
                        result_category = ResultCategory.VerificationWarning,
                        result_key = f"{self.field_name}[{len(results_per_file)}]",
                        result_value = full_path,
                        result_message = "Running `@/exe/bootstrap_env.bash` may leave unversioned unignored symlinks - review and decide to remove or ignore them manually.",
                    ))

            if len(results_per_file) > 0:
                return results_per_file
            else:
                return [CheckEnvResult(
                    result_category = ResultCategory.VerificationSuccess,
                    result_key = self.field_name,
                    result_value = None,
                    result_message = "Clean: no unversioned unignored symlinks.",
                )]
