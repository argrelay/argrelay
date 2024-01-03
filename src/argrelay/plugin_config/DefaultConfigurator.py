from typing import Union

from argrelay.custom_integ.git_utils import is_git_repo, get_shor_commit_id
from argrelay.misc_helper_common import get_argrelay_dir
from argrelay.plugin_config.AbstractConfigurator import AbstractConfigurator


class DefaultConfigurator(AbstractConfigurator):

    def provide_project_git_commit_id(
        self,
    ) -> Union[str, None]:
        argrelay_dir = get_argrelay_dir()
        if is_git_repo(argrelay_dir):
            return get_shor_commit_id(argrelay_dir)
        else:
            return None
