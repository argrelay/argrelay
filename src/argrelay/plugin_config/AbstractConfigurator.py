from typing import Union

from argrelay.enum_desc.PluginType import PluginType
from argrelay.runtime_context.AbstractPlugin import AbstractPlugin


class AbstractConfigurator(AbstractPlugin):
    """
    `PluginType.ConfiguratorPlugin` implements logic to configure `argrelay` server
    when static config is not good enough.
    """

    def get_plugin_type(
        self,
    ) -> PluginType:
        return PluginType.ConfiguratorPlugin

    def provide_project_git_commit_id(
        self,
    ) -> Union[str, None]:
        return None

