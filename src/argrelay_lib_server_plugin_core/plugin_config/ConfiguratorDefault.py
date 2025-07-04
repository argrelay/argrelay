import os
from typing import Union

from argrelay_lib_root.misc_helper_common import get_argrelay_dir
from argrelay_lib_server_plugin_core.plugin_config.ConfiguratorConsistent import (
    ConfiguratorConsistent,
)
from argrelay_lib_server_plugin_core.plugin_config.ConfiguratorDefaultConfigSchema import (
    commit_id_url_prefix_,
    configurator_default_config_desc,
    git_files_by_commit_id_url_prefix_,
    project_page_url_,
    project_title_,
)
from argrelay_lib_server_plugin_demo.demo_git.git_utils import (
    get_commit_time,
    get_full_commit_id,
    get_git_repo_root_path,
    get_short_commit_id,
    is_git_repo,
)


class ConfiguratorDefault(ConfiguratorConsistent):

    def load_config(
        self,
        plugin_config_dict,
    ) -> dict:
        return configurator_default_config_desc.dict_from_input_dict(plugin_config_dict)

    def _provide_project_title(
        self,
    ) -> Union[str, None]:
        if project_title_ in self.plugin_config_dict:
            return self.plugin_config_dict[project_title_]
        else:
            return None

    def _provide_project_page_url(
        self,
    ) -> Union[str, None]:
        if project_page_url_ in self.plugin_config_dict:
            return self.plugin_config_dict[project_page_url_]
        else:
            return None

    def _provide_project_git_files_by_commit_id_url_prefix(
        self,
    ) -> Union[str, None]:
        if git_files_by_commit_id_url_prefix_ in self.plugin_config_dict:
            return self.plugin_config_dict[git_files_by_commit_id_url_prefix_]
        else:
            return None

    def _provide_project_commit_id_url_prefix(
        self,
    ) -> Union[str, None]:
        if commit_id_url_prefix_ in self.plugin_config_dict:
            return self.plugin_config_dict[commit_id_url_prefix_]
        else:
            return None

    def _provide_project_git_commit_id(
        self,
    ) -> Union[str, None]:
        argrelay_dir = get_argrelay_dir()
        if is_git_repo(argrelay_dir):
            return get_full_commit_id(argrelay_dir)
        else:
            return None

    def _provide_project_git_commit_display_string(
        self,
    ) -> Union[str, None]:
        argrelay_dir = get_argrelay_dir()
        if is_git_repo(argrelay_dir):
            return get_short_commit_id(argrelay_dir)
        else:
            return None

    def _provide_project_git_commit_time(
        self,
    ) -> Union[int, None]:
        argrelay_dir = get_argrelay_dir()
        if is_git_repo(argrelay_dir):
            return get_commit_time(argrelay_dir)
        else:
            return None

    def _provide_project_git_repo_relative_argrelay_dir(
        self,
    ) -> Union[str, None]:
        argrelay_dir_abs_path = os.path.realpath(os.path.abspath(get_argrelay_dir()))
        git_repo_root_abs_path = os.path.realpath(
            os.path.abspath(get_git_repo_root_path(get_argrelay_dir()))
        )
        # Make sure argrelay_dir is not outside the git repo:
        if not argrelay_dir_abs_path.startswith(git_repo_root_abs_path):
            return None
        argrelay_dir_rel_path = os.path.relpath(
            argrelay_dir_abs_path, git_repo_root_abs_path
        )
        if argrelay_dir_rel_path == ".":
            # Separator for concatenated path:
            return "/"
        else:
            # Wrap into slashes `/` for concatenation:
            return f"/{argrelay_dir_rel_path}/"

    def _provide_project_current_config_path(
        self,
    ) -> Union[str, None]:
        argrelay_dir = get_argrelay_dir()
        conf_path = os.path.join(argrelay_dir, "conf")
        if os.path.islink(conf_path):
            if os.path.isdir(conf_path):
                argrelay_dir_abs_path = os.path.abspath(get_argrelay_dir())
                project_current_config_path = os.readlink(conf_path)
                project_current_config_abs_path = os.path.abspath(
                    os.path.join(
                        argrelay_dir_abs_path,
                        project_current_config_path,
                    )
                )
                if not project_current_config_abs_path.startswith(
                    argrelay_dir_abs_path
                ):
                    return None
                else:
                    return project_current_config_path
            else:
                return None
        elif os.path.isdir(conf_path):
            return conf_path
        else:
            return None
