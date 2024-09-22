from __future__ import annotations

import re
import subprocess
from typing import Union

from argrelay.check_env.CheckEnvResult import CheckEnvResult
from argrelay.check_env.PluginCheckEnvAbstract import PluginCheckEnvAbstract
from argrelay.enum_desc.ResultCategory import ResultCategory

_common_banner = "Search about GNU Readline (`~/.inputrc`) or `bind` in Bash."
_common_bell_explanation = "Bash sometimes gives terminal \"bell\" instead of showing auto-completion."


class PluginCheckEnvReadlineAbstract(PluginCheckEnvAbstract):
    """
    This plugin checks config of Readline library:
    https://en.wikipedia.org/wiki/GNU_Readline

    Official Bash doc:
    https://www.gnu.org/software/bash/manual/html_node/Readline-Init-File-Syntax.html

    It may be configured via `~/.inputrc` and is used by Bash which can show its settings via `bind -v` command.

    NOTE: Some of these settings may be forced by `@/exe/dev_shell.bash` (set in `@/exe/init_shell_env.bash`),
          but this plugin cannot verify current Bash instance
          (its properties are transient in the memory of its process).
          Instead, it verifies configured properties set for each new Bash instance.
    """

    def __init__(
        self,
        plugin_instance_id: str,
        plugin_config_dict: dict,
        #
        prop_name: str,
        #
        if_on_message: str,
        if_on_category: ResultCategory,
        #
        if_off_message: str,
        if_off_category: ResultCategory,
    ):
        super().__init__(
            plugin_instance_id,
            plugin_config_dict,
        )
        #
        self.prop_name = prop_name
        #
        self.if_on_message = if_on_message
        self.if_on_category = if_on_category
        #
        self.if_off_message = if_off_message
        self.if_off_category = if_off_category

    # noinspection PyMethodMayBeStatic
    def execute_check(
        self,
        online_mode: Union[bool, None],
    ) -> list[CheckEnvResult]:
        try:
            bash_proc = subprocess.run(
                args = [
                    "bash",
                    "-c",
                    "bind -v",
                ],
                capture_output = True,
            )
            assert bash_proc.returncode == 0
            stdout_str = bash_proc.stdout.decode("utf-8")

            prop_value = None
            prop_regex = f"^set\\s*{self.prop_name}\\s*(\\S*)\\s*$"
            for output_line in stdout_str.splitlines():
                regex_match = re.search(prop_regex, output_line, re.M)
                if regex_match:
                    prop_value = regex_match.group(1).strip()
        except:
            prop_value = None

        if "on" == prop_value:
            return [CheckEnvResult(
                result_category = self.if_on_category,
                result_key = self.prop_name,
                result_value = str(prop_value),
                result_message = self.if_on_message,
            )]
        elif "off" == prop_value:
            return [CheckEnvResult(
                result_category = self.if_off_category,
                result_key = self.prop_name,
                result_value = str(prop_value),
                result_message = self.if_off_message,
            )]
        elif prop_value is not None:
            return [CheckEnvResult(
                result_category = ResultCategory.ExecutionFailure,
                result_key = self.prop_name,
                result_value = str(prop_value),
                result_message = f"Unknown value for `{prop_value}` in `bind -v` output.",
            )]
        else:
            return [CheckEnvResult(
                result_category = ResultCategory.ExecutionFailure,
                result_key = self.prop_name,
                result_value = str(prop_value),
                result_message = f"Unable to parse `bind -v` output and find `{prop_value}`.",
            )]


class PluginCheckEnvReadlineShowAllIfAmbiguous(PluginCheckEnvReadlineAbstract):
    """
    See more: https://stackoverflow.com/a/42193784/441652
    """

    def __init__(
        self,
        plugin_instance_id: str,
        plugin_config_dict: dict,
    ):
        prop_name = "show-all-if-ambiguous"
        super().__init__(
            plugin_instance_id,
            plugin_config_dict,
            prop_name = prop_name,
            if_on_message = f"More convenient. {_common_banner}",
            if_on_category = ResultCategory.VerificationSuccess,
            if_off_message = f"Less convenient: if `{prop_name}` is off, {_common_bell_explanation} {_common_banner}",
            if_off_category = ResultCategory.VerificationWarning,
        )


class PluginCheckEnvReadlineShowAllIfUnmodified(PluginCheckEnvReadlineAbstract):
    """
    See more: https://stackoverflow.com/a/42193784/441652
    """

    def __init__(
        self,
        plugin_instance_id: str,
        plugin_config_dict: dict,
    ):
        prop_name = "show-all-if-unmodified"
        super().__init__(
            plugin_instance_id,
            plugin_config_dict,
            prop_name = prop_name,
            if_on_message = f"More convenient. {_common_banner}",
            if_on_category = ResultCategory.VerificationSuccess,
            if_off_message = f"Less convenient: if `{prop_name}` is off, {_common_bell_explanation} {_common_banner}",
            if_off_category = ResultCategory.VerificationWarning,
        )


class PluginCheckEnvReadlineSkipCompletedText(PluginCheckEnvReadlineAbstract):

    def __init__(
        self,
        plugin_instance_id: str,
        plugin_config_dict: dict,
    ):
        prop_name = "skip-completed-text"
        super().__init__(
            plugin_instance_id,
            plugin_config_dict,
            prop_name = prop_name,
            if_on_message = f"More convenient. {_common_banner}",
            if_on_category = ResultCategory.VerificationSuccess,
            if_off_message = f"Less convenient: if `{prop_name}` is off, inserting completed CLI arg part will duplicate existing one. {_common_banner}",
            if_off_category = ResultCategory.VerificationWarning,
        )
