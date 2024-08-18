import argrelay
from argrelay.check_env.CheckEnvResult import CheckEnvResult
from argrelay.check_env.PluginCheckEnvServerResponseValueAbstract import PluginCheckEnvServerResponseValueAbstract
from argrelay.custom_integ.SchemaPluginCheckEvnServerResponseValueAbstract import field_values_to_command_lines_
from argrelay.enum_desc.CheckEnvField import CheckEnvField
from argrelay.enum_desc.ResultCategory import ResultCategory


class PluginCheckEnvServerResponseValueVersion(PluginCheckEnvServerResponseValueAbstract):
    # TODO: TODO_69_59_78_78: register known files as enum with metadata:
    bootstrap_rel_path = "exe/bootstrap_env.bash"

    def __init__(
        self,
        plugin_instance_id: str,
        plugin_config_dict: dict,
    ):
        super().__init__(
            plugin_instance_id,
            plugin_config_dict = plugin_config_dict or {
                field_values_to_command_lines_: {
                    CheckEnvField.server_version.name: "argrelay.check_env server_version",
                },
            },
        )

    def verify_online_value(
        self,
        field_name: str,
        field_value,
    ) -> CheckEnvResult:
        client_version = argrelay.__version__

        if client_version == field_value:
            return CheckEnvResult(
                result_category = ResultCategory.VerificationSuccess,
                result_key = field_name,
                result_value = field_value,
                result_message = f"It matches client `argrelay_module_version`",
            )
        else:
            return CheckEnvResult(
                result_category = ResultCategory.VerificationWarning,
                result_key = field_name,
                result_value = field_value,
                result_message = f"It does not match client `argrelay_module_version` => re-base and re-run `@/{self.bootstrap_rel_path}`",
            )
