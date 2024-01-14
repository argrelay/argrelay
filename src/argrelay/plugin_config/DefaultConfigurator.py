from typing import Union

from argrelay.custom_integ.git_utils import (
    is_git_repo,
    get_full_commit_id,
    get_short_commit_id,
    get_commit_time,
)
from argrelay.misc_helper_common import get_argrelay_dir
from argrelay.plugin_config.AbstractConfigurator import AbstractConfigurator
from argrelay.plugin_config.DefaultConfiguratorConfigSchema import (
    default_configurator_config_desc,
    commit_id_url_prefix_,
)


class DefaultConfigurator(AbstractConfigurator):

    def load_config(
        self,
        plugin_config_dict,
    ) -> dict:
        # TODO_74_03_78_60: Call `TypeDesc` API to do load (to populate defaults) -> dump automatically.
        return default_configurator_config_desc.dict_schema.dump(
            default_configurator_config_desc.dict_schema.load(
                plugin_config_dict,
            ),
        )

    def provide_project_commit_id_url_prefix(
        self,
    ) -> Union[str, None]:
        if commit_id_url_prefix_ in self.plugin_config_dict:
            return self.plugin_config_dict[commit_id_url_prefix_]
        else:
            return None

    def provide_project_git_commit_id(
        self,
    ) -> Union[str, None]:
        argrelay_dir = get_argrelay_dir()
        if is_git_repo(argrelay_dir):
            return get_full_commit_id(argrelay_dir)
        else:
            return None

    def provide_project_git_commit_display_string(
        self,
    ) -> Union[str, None]:
        argrelay_dir = get_argrelay_dir()
        if is_git_repo(argrelay_dir):
            return get_short_commit_id(argrelay_dir)
        else:
            return None

    def provide_project_git_commit_time(
        self,
    ) -> Union[int, None]:
        argrelay_dir = get_argrelay_dir()
        if is_git_repo(argrelay_dir):
            return get_commit_time(argrelay_dir)
        else:
            return None
