from typing import Union

from argrelay_api_plugin_server_abstract.AbstractPluginServer import AbstractPluginServer
from argrelay_lib_root.enum_desc.PluginType import PluginType


class ConfiguratorAbstract(AbstractPluginServer):
    """
    `PluginType.ConfiguratorPlugin` implements logic to configure `argrelay` server
    when static config is not good enough.
    """

    def get_plugin_type(
        self,
    ) -> PluginType:
        return PluginType.ConfiguratorPlugin

    def provide_project_title(
        self,
    ) -> Union[str, None]:
        """
        Names an instance of `argrelay`.
        """
        return None

    def provide_project_page_url(
        self,
    ) -> Union[str, None]:
        """
        Project a URL to project page.
        """
        return None

    def provide_project_git_commit_display_string(
        self,
    ) -> Union[str, None]:
        """
        Returns commit id (in any format) to be shown as is.

        This commit display string is used as text for a link (purely display function).

        The link itself is generated by concatenating two components - see:
        *   `provide_project_commit_id_url_prefix`
        *   `provide_project_git_commit_id`
        """
        return None

    def provide_project_git_files_by_commit_id_url_prefix(
        self,
    ) -> Union[str, None]:
        """
        Returns a URL prefix to form valid URL by concatenation of:
        *   `provide_project_git_files_by_commit_id_url_prefix`
        *   `provide_project_git_commit_id`
        *   `provide_project_git_repo_relative_argrelay_dir`
        *   `provide_project_current_config_path`

        For example:
        https://github.com/argrelay/argrelay/tree/
        to be used for:
        https://github.com/argrelay/argrelay/tree/ba1e6c684c476558181a8e127d9c34f1feaf5cde/dst/.github
        """
        return None

    def provide_project_commit_id_url_prefix(
        self,
    ) -> Union[str, None]:
        """
        Returns a URL prefix to form valid URL by concatenation with:
        *   `provide_project_git_commit_id`

        The display text for the link is taken from `provide_project_git_commit_display_string` instead.

        For example:
        https://github.com/argrelay/argrelay/commit/
        to be used for:
        https://github.com/argrelay/argrelay/commit/70bf34b3f773b576c8153ada9ea3baa5b228b8a0
        """
        return None

    def provide_project_git_commit_id(
        self,
    ) -> Union[str, None]:
        """
        Returns commit id in specific format (e.g. full) which should work as part of a URL.

        It is concatenated with `provide_project_git_commit_id_url_prefix` to form a URL.

        The display text for the link is taken from `provide_project_git_commit_display_string` instead.
        """
        return None

    def provide_project_git_commit_time(
        self,
    ) -> Union[int, None]:
        """
        Return commit time in seconds since epoch (Unix time).

        The commit time should normally be taken for the same commit id as `provide_project_git_commit_id`.
        """
        return None

    def provide_project_git_repo_relative_argrelay_dir(
        self,
    ) -> Union[str, None]:
        """
        Return relative path of `argrelay_dir` within project git repo.

        It is used to provide link to config files by concatenation of:
        *   `provide_project_git_files_by_commit_id_url_prefix`
        *   `provide_project_git_commit_id`
        *   `provide_project_git_repo_relative_argrelay_dir`
        *   `provide_project_current_config_path`
        """
        return None

    def provide_project_current_config_path(
        self,
    ) -> Union[str, None]:
        """
        Returns path where `@/conf/` symlink points to (or `conf` str directly if `@/conf/` is a dir).

        The path is relative to `argrelay_dir` (`@/`).

        The purpose is to compose a valid URL concatenating it with other parts.
        For this to work, `@/conf/` should be a symlink with relative path (pointing inside `argrelay_dir`).

        It is used to provide link to config files by concatenation of:
        *   `provide_project_git_files_by_commit_id_url_prefix`
        *   `provide_project_git_commit_id`
        *   `provide_project_git_repo_relative_argrelay_dir`
        *   `provide_project_current_config_path`
        """
        return None