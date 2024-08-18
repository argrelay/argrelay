from argrelay.check_env.CheckEnvResult import CheckEnvResult
from argrelay.check_env.PluginCheckEnvServerResponseValueAbstract import PluginCheckEnvServerResponseValueAbstract
from argrelay.custom_integ.SchemaPluginCheckEvnServerResponseValueAbstract import field_values_to_command_lines_
from argrelay.custom_integ.git_utils import is_git_repo, get_full_commit_id
from argrelay.enum_desc.CheckEnvField import CheckEnvField
from argrelay.enum_desc.ResultCategory import ResultCategory
from argrelay.misc_helper_common import get_argrelay_dir

_commit_id_display_length = 8


class PluginCheckEnvServerResponseValueCommitId(PluginCheckEnvServerResponseValueAbstract):

    def __init__(
        self,
        plugin_instance_id: str,
        plugin_config_dict: dict,
    ):
        super().__init__(
            plugin_instance_id,
            plugin_config_dict = plugin_config_dict or {
                field_values_to_command_lines_: {
                    CheckEnvField.server_git_commit_id.name: "argrelay.check_env server_commit",
                },
            },
        )

    def verify_online_value(
        self,
        field_name: str,
        field_value,
    ) -> CheckEnvResult:
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
                result_message = "Failed on getting client commit id",
            )
        else:
            if client_commit_id == field_value:
                return CheckEnvResult(
                    result_category = ResultCategory.VerificationSuccess,
                    result_key = field_name,
                    result_value = field_value[:_commit_id_display_length],
                    result_message = f"The runtime server commit id matches client one [{client_commit_id[:_commit_id_display_length]}]",
                )
            else:
                return CheckEnvResult(
                    result_category = ResultCategory.VerificationWarning,
                    result_key = field_name,
                    result_value = field_value[:_commit_id_display_length],
                    result_message = f"The runtime server commit id does not match client one [{client_commit_id[:_commit_id_display_length]}]",
                )
