from argrelay.check_env.CheckEnvResult import CheckEnvResult
from argrelay.check_env.PluginCheckEnvServerResponseValueAbstract import PluginCheckEnvServerResponseValueAbstract
from argrelay.custom_integ.SchemaPluginCheckEvnServerResponseValueAbstract import field_values_to_command_lines_
from argrelay.custom_integ.git_utils import is_git_repo, get_full_commit_id
from argrelay.enum_desc.CheckEnvField import CheckEnvField
from argrelay.enum_desc.ResultCategory import ResultCategory
from argrelay.misc_helper_common import get_argrelay_dir


class PluginCheckEnvServerResponseValueCommitId(PluginCheckEnvServerResponseValueAbstract):

    def __init__(
        self,
        plugin_instance_id: str,
        plugin_config_dict: dict,
    ):
        super().__init__(
            plugin_instance_id,
            plugin_config_dict = plugin_config_dict or {
                # TODO: Maybe remove this class and simply rely on config?
                field_values_to_command_lines_: {
                    CheckEnvField.server_git_commit_id.name: "argrelay.check_env server_commit",
                },
            },
        )

    def verify_value(
        self,
        field_name,
        field_value,
    ) -> CheckEnvResult:
        if field_name == CheckEnvField.server_git_commit_id.name:

            argrelay_dir = get_argrelay_dir()

            if is_git_repo(argrelay_dir):
                try:
                    client_commit_id = get_full_commit_id(argrelay_dir)
                except ValueError:
                    client_commit_id = None
            else:
                client_commit_id = None

            if client_commit_id is None:
                return CheckEnvResult(
                    result_category = ResultCategory.ExecutionFailure,
                    result_key = field_name,
                    result_value = field_value,
                    result_message = "failed on getting client commit id",
                )
            else:
                if client_commit_id == field_value:
                    return CheckEnvResult(
                        result_category = ResultCategory.VerificationSuccess,
                        result_key = field_name,
                        result_value = field_value,
                        result_message = f"client commit id [{client_commit_id}] matches server commit id",
                    )
                else:
                    return CheckEnvResult(
                        result_category = ResultCategory.VerificationWarning,
                        result_key = field_name,
                        result_value = field_value,
                        result_message = f"client commit id [{client_commit_id}] does not match server commit id [{field_value}]",
                    )
        else:
            return super().verify_value(
                field_name,
                field_value,
            )
