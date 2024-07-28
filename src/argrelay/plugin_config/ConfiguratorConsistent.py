import inspect
from typing import Union

from argrelay.plugin_config.ConfiguratorAbstract import ConfiguratorAbstract
from argrelay.runtime_data.ServerConfig import ServerConfig


class ConfiguratorConsistent(ConfiguratorAbstract):
    """
    Query all values on start (on activation) and consistently reply the same value on next queries.

    This is to ensure that, for example, the same git commit id is reported
    matching server runtime rather than current disk state.
    """

    def __init__(
        self,
        server_config: ServerConfig,
        plugin_instance_id: str,
        plugin_config_dict: dict,
    ):
        super().__init__(
            server_config,
            plugin_instance_id,
            plugin_config_dict,
        )
        self.consistent_replies: dict[str, Union[str, None]] = {}

    def activate_plugin(
        self,
    ) -> None:
        """
        Call all funcs to store their values for subsequent calls.
        """
        for func_obj in [
            self.provide_project_title,
            self.provide_project_page_url,
            self.provide_project_git_commit_display_string,
            self.provide_project_git_files_by_commit_id_url_prefix,
            self.provide_project_commit_id_url_prefix,
            self.provide_project_git_commit_id,
            self.provide_project_git_commit_time,
            self.provide_project_git_repo_relative_argrelay_dir,
            self.provide_project_current_config_path,
        ]:
            func_obj()

    def reply_consistently(
        self,
    ):
        """
        If replied once with one answer, repeat this answer subsequently.
        """

        caller_func_name = inspect.currentframe().f_back.f_code.co_name
        if caller_func_name not in self.consistent_replies:
            # Call "protected" func to get value:
            func_reply = getattr(self, f"_{caller_func_name}")()
            self.consistent_replies[caller_func_name] = func_reply
            return func_reply
        else:
            return self.consistent_replies[caller_func_name]

    ####################################################################################################################

    def provide_project_title(
        self,
    ) -> Union[str, None]:
        return self.reply_consistently()

    def _provide_project_title(
        self,
    ) -> Union[str, None]:
        return None

    ####################################################################################################################

    def provide_project_page_url(
        self,
    ) -> Union[str, None]:
        return self.reply_consistently()

    def _provide_project_page_url(
        self,
    ) -> Union[str, None]:
        return None

    ####################################################################################################################

    def provide_project_git_commit_display_string(
        self,
    ) -> Union[str, None]:
        return self.reply_consistently()

    def _provide_project_git_commit_display_string(
        self,
    ) -> Union[str, None]:
        return None

    ####################################################################################################################

    def provide_project_git_files_by_commit_id_url_prefix(
        self,
    ) -> Union[str, None]:
        return self.reply_consistently()

    def _provide_project_git_files_by_commit_id_url_prefix(
        self,
    ) -> Union[str, None]:
        return None

    ####################################################################################################################

    def provide_project_commit_id_url_prefix(
        self,
    ) -> Union[str, None]:
        return self.reply_consistently()

    def _provide_project_commit_id_url_prefix(
        self,
    ) -> Union[str, None]:
        return None

    ####################################################################################################################

    def provide_project_git_commit_id(
        self,
    ) -> Union[str, None]:
        return self.reply_consistently()

    def _provide_project_git_commit_id(
        self,
    ) -> Union[str, None]:
        return None

    ####################################################################################################################

    def provide_project_git_commit_time(
        self,
    ) -> Union[int, None]:
        return self.reply_consistently()

    def _provide_project_git_commit_time(
        self,
    ) -> Union[int, None]:
        return None

    ####################################################################################################################

    def provide_project_git_repo_relative_argrelay_dir(
        self,
    ) -> Union[str, None]:
        return self.reply_consistently()

    def _provide_project_git_repo_relative_argrelay_dir(
        self,
    ) -> Union[str, None]:
        return None

    ####################################################################################################################

    def provide_project_current_config_path(
        self,
    ) -> Union[str, None]:
        return self.reply_consistently()

    def _provide_project_current_config_path(
        self,
    ) -> Union[str, None]:
        return None

    ####################################################################################################################
