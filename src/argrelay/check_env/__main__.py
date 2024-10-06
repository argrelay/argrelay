"""
Python part of FS_36_17_84_44 `check_env` implementation.
"""

import os
import sys

from argrelay import misc_helper_common
from argrelay.check_env.CheckEnvResult import CheckEnvResult
from argrelay.check_env.PluginCheckEnvAbstract import PluginCheckEnvAbstract
from argrelay.enum_desc.OutputCategory import OutputCategory
from argrelay.enum_desc.PluginSide import PluginSide
from argrelay.enum_desc.PluginType import PluginType
from argrelay.enum_desc.ResultCategory import ResultCategory
from argrelay.enum_desc.TermColor import TermColor
from argrelay.relay_client.client_utils import handle_main_exception
from argrelay.runtime_context.PluginClientAbstract import instantiate_client_plugin
from argrelay.runtime_data.CheckEnvPluginConfig import CheckEnvPluginConfig
from argrelay.runtime_data.PluginEntry import PluginEntry
from argrelay.schema_config_plugin.CheckEnvPluginConfigSchema import check_env_plugin_config_desc

# Standard color scheme has to be synced with `@/exe/check_env.bash`:
success_color = f"{TermColor.back_dark_green.value}{TermColor.fore_dark_black.value}"
warning_color = f"{TermColor.back_dark_yellow.value}{TermColor.fore_dark_black.value}"
failure_color = f"{TermColor.back_dark_red.value}{TermColor.fore_bright_white.value}"
field_color = TermColor.fore_bright_cyan.value
failure_message = TermColor.fore_dark_red.value
warning_message = TermColor.fore_bright_yellow.value
success_message = TermColor.fore_bright_green.value
reset_style = TermColor.reset_style.value

# Extra color scheme (available via Python code only):
offline_color = f"{TermColor.back_light_gray.value}{TermColor.fore_dark_black.value}"
offline_message = TermColor.fore_bright_magenta.value


# TODO: TODO_67_33_03_53.add_check_env_test_support.md
def main():
    # noinspection PyBroadException
    try:
        return check_env_logic()
    except BaseException as e1:
        handle_main_exception(e1)


def check_env_logic():
    argrelay_dir: str = os.path.realpath(os.path.abspath(sys.argv[1]))
    misc_helper_common.set_argrelay_dir(argrelay_dir)

    dry_run = False
    online_mode = None

    if len(sys.argv) > 3:
        raise ValueError(f"too many arguments: {' '.join(sys.argv[1:])}")
    elif len(sys.argv) == 3:
        second_arg = sys.argv[2].strip()
        if second_arg == "offline":
            online_mode = False
        elif second_arg == "online":
            online_mode = True
        elif second_arg == "dry_run":
            dry_run = True
        else:
            raise ValueError(f"unrecognized argument: {second_arg}")
    else:
        online_mode = None

    plugin_config: CheckEnvPluginConfig = check_env_plugin_config_desc.obj_from_default_file()

    total_success: bool = True

    for plugin_instance_id in plugin_config.check_env_plugin_instance_id_activate_list:
        plugin_entry: PluginEntry = plugin_config.check_env_plugin_instances[plugin_instance_id]

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

        if dry_run:
            continue

        check_env_results: list[CheckEnvResult] = plugin_instance.execute_check(
            online_mode,
        )
        for check_env_result in check_env_results:
            total_success: bool = print_output_line(check_env_result, total_success)

    if not total_success:
        from argrelay.enum_desc.ClientExitCode import ClientExitCode
        exit(ClientExitCode.GeneralError.value)


def print_output_line(
    check_env_result: CheckEnvResult,
    total_success: bool,
):
    if (
        check_env_result.result_category is ResultCategory.ExecutionFailure
        or
        check_env_result.result_category is ResultCategory.VerificationFailure
    ):
        output_category = OutputCategory.is_failure
    elif check_env_result.result_category is ResultCategory.ServerOffline:
        output_category = OutputCategory.is_offline
    elif check_env_result.result_category is ResultCategory.VerificationWarning:
        output_category = OutputCategory.is_warning
    elif check_env_result.result_category is ResultCategory.VerificationSuccess:
        output_category = OutputCategory.is_success
    else:
        raise RuntimeError(check_env_result)
    total_success = total_success and not (output_category is OutputCategory.is_failure)

    # Print level:
    if output_category is OutputCategory.is_failure:
        level_color = failure_color
        level_name = "ERROR"
    elif output_category is OutputCategory.is_offline:
        level_color = offline_color
        level_name = "SKIP"
    elif output_category is OutputCategory.is_warning:
        level_color = warning_color
        level_name = "WARN"
    else:
        level_color = success_color
        level_name = "INFO"
    print(f"{level_color}{level_name}:{reset_style}", end = " ")

    # Print field:
    if check_env_result.result_key is not None:
        print(f"{field_color}{check_env_result.result_key}:{reset_style}", end = " ")
    else:
        pass

    # Print value:
    if check_env_result.result_value is not None:
        print(f"{check_env_result.result_value}", end = " ")
    else:
        pass

    # Print message:
    if check_env_result.result_message is not None:
        if output_category is OutputCategory.is_failure:
            message_color = failure_message
        elif output_category is OutputCategory.is_offline:
            message_color = offline_message
        elif output_category is OutputCategory.is_warning:
            message_color = warning_message
        else:
            message_color = success_message
        print(f"{message_color}# {check_env_result.result_message}{reset_style}", end = " ")
    else:
        pass

    # Terminate line:
    print()

    return total_success


if __name__ == "__main__":
    main()
