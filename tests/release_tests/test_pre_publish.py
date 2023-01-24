"""
Check things which should not be published

For example, `GitRepoLoader` should not be enabled in `argrelay.server.yaml`.
"""
import os
from unittest import TestCase

from argrelay.relay_demo import GitRepoLoader as GitRepoLoader_module
from argrelay.relay_demo.GitRepoLoader import GitRepoLoader as GitRepoLoader_class
from argrelay.relay_demo.GitRepoLoaderConfigSchema import is_enabled_
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.schema_config_core_server.ServerConfigSchema import (
    server_config_desc,
)
from argrelay.test_helper import change_to_known_path_tests_dir


class ThisTestCase(TestCase):

    def test_git_repo_loader_is_disabled(self):
        """
        `GitRepoLoader` should not be enabled in `argrelay.server.yaml`.
        """

        server_config: ServerConfig = server_config_desc.from_default_file()
        found_one = False
        git_loader_plugin = None
        for plugin_id in server_config.plugin_id_load_list:
            plugin_item = server_config.plugin_dict[plugin_id]
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

    def test_env_tests_have_no_init_file(self):
        """
        There should be no `__init__.py` file under `env_tests` directory.

        This keeps all tests under `env_tests` non-discoverable when run from `env_tests`.

        See `tests/readme.md`.
        """

        change_to_known_path_tests_dir()

        self.assertTrue(os.path.isdir("env_tests"))
        self.assertFalse(os.path.exists("env_tests/__init__.py"))
