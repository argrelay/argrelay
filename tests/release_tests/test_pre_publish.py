from __future__ import annotations

import os
from typing import Union
from unittest import skipIf

from argrelay_lib_server_plugin_demo.demo_git import (
    GitRepoLoader as GitRepoLoader_module,
)
from argrelay_lib_server_plugin_demo.demo_git.GitRepoLoader import (
    GitRepoLoader as GitRepoLoader_class,
)
from argrelay_schema_config_server.runtime_data_server_plugin.PluginConfig import (
    PluginConfig,
)
from argrelay_schema_config_server.runtime_data_server_plugin.PluginEntry import (
    PluginEntry,
)
from argrelay_schema_config_server.schema_config_server_plugin.PluginConfigSchema import (
    plugin_config_desc,
)
from argrelay_test_infra.test_infra import change_to_known_repo_path
from argrelay_test_infra.test_infra.BaseTestClass import BaseTestClass
from argrelay_test_infra.test_infra.EnvMockBuilder import ServerOnlyEnvMockBuilder


class ThisTestClass(BaseTestClass):
    """
    Check things which should not be published

    For example, `GitRepoLoader` should not be enabled in `argrelay_plugin.yaml`.
    """

    def test_default_git_repo_loader_is_disabled(self):
        """
        `GitRepoLoader.default` should not be enabled in `argrelay_plugin.yaml`.

        `GitRepoLoader.self` can be enabled.
        """

        # Still use mock because config data for the mock is loaded from source files:
        # * `load_custom_integ_client_config_dict`
        # * `load_custom_integ_server_config_dict`
        # * `load_custom_integ_plugin_config_dict`
        env_mock_builder = (
            ServerOnlyEnvMockBuilder()
            # This test does not use server code and loads plugin config directly - disable mocking server config load:
            .set_mock_server_config_file_read(False).clear_server_config_dict()
        )
        with env_mock_builder.build():

            plugin_config: PluginConfig = plugin_config_desc.obj_from_default_file()
            found_one = False
            git_loader_plugin_entry: Union[PluginEntry, None] = None
            for plugin_instance_id in plugin_config.plugin_instance_id_activate_list:
                plugin_entry: PluginEntry = plugin_config.server_plugin_instances[
                    plugin_instance_id
                ]
                if (
                    plugin_entry.plugin_module_name == GitRepoLoader_module.__name__
                    and plugin_entry.plugin_class_name == GitRepoLoader_class.__name__
                ):
                    if ".self" in plugin_instance_id:
                        # Ignore ".self" - it is allowed:
                        pass
                    else:
                        if found_one:
                            raise RuntimeError(
                                "two " + GitRepoLoader_class.__name__ + " plugins?"
                            )
                        found_one = True
                        git_loader_plugin_entry = plugin_entry
            if not found_one:
                raise RuntimeError(
                    "missing " + GitRepoLoader_class.__name__ + " plugin?"
                )

            self.assertFalse(git_loader_plugin_entry.plugin_enabled)

    def test_env_tests_have_no_init_file(self):
        """
        There should be no `__init__.py` file under `env_tests` directory.

        This keeps all tests under `env_tests` non-discoverable when run from `env_tests`.

        See `tests/readme.md`.
        """

        with change_to_known_repo_path():
            self.assertTrue(os.path.isdir("env_tests"))
            self.assertFalse(os.path.exists("env_tests/__init__.py"))

    def test_config_base_dir_is_not_overridden(self):
        """
        `ARGRELAY_CONF_BASE_DIR` should not be defined

        This is to ensure clean env (without overrides) works as priority.
        """

        self.assertTrue("ARGRELAY_CONF_BASE_DIR" not in os.environ)

    @skipIf(
        (
            (os.environ.get("ARGRELAY_DEV_SHELL", False))
            or (os.environ.get("ARGRELAY_BOOTSTRAP_ENV", False))
            or (os.environ.get("PYCHARM_HOSTED", False))
        ),
        "To allow installed config files, skip when in `@/exe/dev_shell.bash` or in IDE.",
    )
    def test_config_files_are_not_installed(self):
        """
        TODO: This test is old - search all dirs according to `FS_16_07_78_84.conf_dir_priority.md`.

        Ensure server and client config files are not installed:

        *   `~/.argrelay.conf.d/argrelay_client.json`
        *   `~/.argrelay.conf.d/argrelay_server.yaml`
        *   `~/.argrelay.conf.d/argrelay_plugin.yaml`
        *   `~/.argrelay.conf.d/check_env_plugin.conf.bash`
        *   `~/.argrelay.conf.d/check_env_plugin.conf.yaml`

        Move them under different name to preserve or delete them completely.

        This, in turn ensures that no other tests rely on their existence (and use proper file access mocking).

        Note that `test_config_base_dir_is_not_overridden` ensures that we only need to test for ~ = user home.
        """

        for file_path in [
            os.path.expanduser("~") + "/.argrelay.conf.d/argrelay_client.json",
            os.path.expanduser("~") + "/.argrelay.conf.d/argrelay_server.yaml",
            os.path.expanduser("~") + "/.argrelay.conf.d/argrelay_plugin.yaml",
            os.path.expanduser("~") + "/.argrelay.conf.d/check_env_plugin.conf.bash",
            os.path.expanduser("~") + "/.argrelay.conf.d/check_env_plugin.conf.yaml",
        ]:
            self.assertFalse(os.path.exists(file_path))

    # TODO: Run test-loading other than default demo data.
