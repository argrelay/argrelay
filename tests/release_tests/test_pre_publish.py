"""
Check things which should not be published

For example, `GitRepoLoader` should not be enabled in `argrelay.server.yaml`.
"""
from unittest import TestCase

from argrelay.meta_data.ServerConfig import ServerConfig
from argrelay.relay_demo import GitRepoLoader as GitRepoLoader_module
from argrelay.relay_demo.GitRepoLoader import GitRepoLoader as GitRepoLoader_class
from argrelay.relay_demo.GitRepoLoaderConfigSchema import is_enabled_
from argrelay.schema_config_core_server.ServerConfigSchema import (
    server_config_desc,
)


class ThisTestCase(TestCase):

    def test_git_repo_loader_is_disabled(self):
        """
        `GitRepoLoader` should not be enabled in `argrelay.server.yaml`.
        """

        server_config: ServerConfig = server_config_desc.from_default_file()
        found_one = False
        git_loader_plugin = None
        for plugin_item in server_config.plugin_list:
            if (
                plugin_item.plugin_module_name == GitRepoLoader_module.__name__
                and
                plugin_item.plugin_class_name == GitRepoLoader_class.__name__
            ):
                if found_one:
                    raise RuntimeError("two " + GitRepoLoader_class.__name__ + " plugins?")
                found_one = True
                git_loader_plugin = plugin_item
        if not found_one:
            raise RuntimeError("missing " + GitRepoLoader_class.__name__ + " plugin?")

        self.assertFalse(git_loader_plugin.plugin_config[is_enabled_])
