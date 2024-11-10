import time
from datetime import datetime, timezone

from argrelay.check_env.CheckEnvResult import CheckEnvResult
from argrelay.check_env.PluginCheckEnvServerResponseValueAbstract import PluginCheckEnvServerResponseValueAbstract
from argrelay.check_env.check_env_utils import format_time_to_relative
from argrelay.custom_integ.SchemaPluginCheckEvnServerResponseValueAbstract import field_values_to_command_lines_
from argrelay.enum_desc.CheckEnvField import CheckEnvField


class PluginCheckEnvServerResponseValueStartTime(PluginCheckEnvServerResponseValueAbstract):

    def __init__(
        self,
        plugin_instance_id: str,
        plugin_config_dict: dict,
    ):
        super().__init__(
            plugin_instance_id,
            plugin_config_dict = plugin_config_dict or {
                field_values_to_command_lines_: {
                    CheckEnvField.server_start_time.name: "argrelay.check_env server_start_time",
                },
            },
        )

    def verify_online_value(
        self,
        field_name,
        field_value,
    ) -> CheckEnvResult:
        check_env_result: CheckEnvResult = super().verify_online_value(
            field_name,
            field_value,
        )
        # Put formated time to the message:
        if check_env_result.result_category.VerificationSuccess:
            utc_time = datetime.fromtimestamp(int(field_value), timezone.utc)
            epoch_start = datetime.fromtimestamp(0, timezone.utc)

            # Local timezone:
            abs_time_str = utc_time.astimezone(None).isoformat()
            rel_time_str = format_time_to_relative(
                time.time() * 1000,
                (utc_time - epoch_start).total_seconds() * 1000,
            )

            check_env_result.result_message = f"{abs_time_str} ~ {rel_time_str}"
        return check_env_result
