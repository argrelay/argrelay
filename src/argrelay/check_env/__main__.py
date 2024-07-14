"""
Python part of FS_36_17_84_44 `check_env` implementation.
"""

import os
import sys

from argrelay import misc_helper_common
from argrelay.check_env.CheckEnvResult import CheckEnvResult
from argrelay.check_env.PluginCheckEnvAbstract import PluginCheckEnvAbstract
from argrelay.enum_desc.PluginSide import PluginSide
from argrelay.enum_desc.PluginType import PluginType
from argrelay.enum_desc.ResultCategory import ResultCategory
from argrelay.enum_desc.TermColor import TermColor
from argrelay.misc_helper_common import eprint
from argrelay.runtime_context.PluginClientAbstract import instantiate_client_plugin
from argrelay.runtime_data.PluginConfig import PluginConfig
from argrelay.runtime_data.PluginEntry import PluginEntry
from argrelay.schema_config_plugin.PluginConfigSchema import plugin_config_desc

# Color scheme has to be synced with `@/exe/check_env.bash`:
success_color = TermColor.back_dark_green.value
warning_color = TermColor.back_dark_yellow.value
failure_color = TermColor.back_dark_red.value
field_color = TermColor.fore_bright_cyan.value
failure_message = TermColor.fore_dark_red.value
warning_message = TermColor.fore_bright_yellow.value
success_message = TermColor.fore_bright_green.value
reset_style = TermColor.reset_style.value


# TODO: TODO_67_33_03_53.add_check_env_test_support.md
def main():
    argrelay_dir: str = os.path.realpath(os.path.abspath(sys.argv[1]))
    misc_helper_common.set_argrelay_dir(argrelay_dir)

    plugin_config: PluginConfig = plugin_config_desc.obj_from_default_file()

    total_success: bool = True

    for plugin_instance_id in plugin_config.plugin_instance_id_activate_list:
        plugin_entry: PluginEntry = plugin_config.plugin_instance_entries[plugin_instance_id]

        if not plugin_entry.plugin_enabled:
            continue

        if (
            plugin_entry.plugin_side != PluginSide.PluginClientSideOnly
            and
            plugin_entry.plugin_side != PluginSide.PluginAnySide
        ):
            continue

        plugin_instance: PluginCheckEnvAbstract = instantiate_client_plugin(
            plugin_instance_id,
            plugin_entry,
        )
        plugin_type = plugin_instance.get_plugin_type()

        if plugin_type is PluginType.CheckEnvPlugin:
            plugin_instance: PluginCheckEnvAbstract
            plugin_instance.activate_plugin()

        check_env_results: list[CheckEnvResult] = plugin_instance.execute_check()
        for check_env_result in check_env_results:
            is_failure: bool = (
                check_env_result.result_category is ResultCategory.ExecutionFailure
                or
                check_env_result.result_category is ResultCategory.VerificationFailure
            )
            is_warning: bool = check_env_result.result_category is ResultCategory.VerificationWarning

            total_success = total_success and not is_failure

            # Print level:
            if is_failure:
                eprint(f"{failure_color}ERROR:{reset_style}", end = " ")
            else:
                if is_warning:
                    eprint(f"{warning_color}WARN:{reset_style}", end = " ")
                else:
                    eprint(f"{success_color}INFO:{reset_style}", end = " ")

            # Print field:
            if check_env_result.result_key is not None:
                eprint(f"{field_color}{check_env_result.result_key}:{reset_style}", end = " ")
            else:
                pass

            # Print value:
            if check_env_result.result_value is not None:
                eprint(f"{check_env_result.result_value}", end = " ")
            else:
                pass

            # Print message:
            if check_env_result.result_message is not None:
                if is_failure:
                    eprint(f"{failure_message}# {check_env_result.result_message}{reset_style}", end = " ")
                else:
                    if is_warning:
                        eprint(f"{warning_message}# {check_env_result.result_message}{reset_style}", end = " ")
                    else:
                        eprint(f"{success_message}# {check_env_result.result_message}{reset_style}", end = " ")
            else:
                pass

            # Terminate line:
            eprint()

    if total_success:
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()
