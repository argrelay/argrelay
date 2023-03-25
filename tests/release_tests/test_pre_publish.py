"""
Check things which should not be published

For example, `GitRepoLoader` should not be enabled in `argrelay.server.yaml`.
"""
import os
from unittest import TestCase, skipIf

from argrelay.custom_integ import GitRepoLoader as GitRepoLoader_module
from argrelay.custom_integ.GitRepoLoader import GitRepoLoader as GitRepoLoader_class
from argrelay.custom_integ.GitRepoLoaderConfigSchema import is_plugin_enabled_
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.schema_config_core_server.ServerConfigSchema import (
    server_config_desc,
)
from argrelay.test_helper import change_to_known_repo_path
from argrelay.test_helper.EnvMockBuilder import EnvMockBuilder


class ThisTestCase(TestCase):

    def test_git_repo_loader_is_disabled(self):
        """
        `GitRepoLoader` should not be enabled in `argrelay.server.yaml`.
        """

        # Still use mock because config data for the mock is loaded from source files:
        # * `load_custom_integ_server_config_dict`
        # * `load_custom_integ_client_config_dict`
        env_mock_builder = (
            EnvMockBuilder()
            # TODO: have pre-configured mocks: with client, without client, any other variants?
            # Not running the client in ths test:
            .set_client_config_with_local_server(False)
            .set_mock_client_config_file_read(False)
        )
        with env_mock_builder.build():

            server_config: ServerConfig = server_config_desc.from_default_file()
            found_one = False
            git_loader_plugin = None
            for plugin_instance_id in server_config.plugin_instance_id_load_list:
                plugin_item = server_config.plugin_dict[plugin_instance_id]
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

            self.assertFalse(git_loader_plugin.plugin_config[is_plugin_enabled_])

    def test_env_tests_have_no_init_file(self):
        """
        There should be no `__init__.py` file under `env_tests` directory.

        This keeps all tests under `env_tests` non-discoverable when run from `env_tests`.

        See `tests/readme.md`.
        """

        with change_to_known_repo_path():
            self.assertTrue(os.path.isdir("env_tests"))
            self.assertFalse(os.path.exists("env_tests/__init__.py"))

    def test_config_base_dir_is_not_overriden(self):
        """
        `ARGRELAY_CONF_BASE_DIR` should not be defined

        This is to ensure clean env (without overrides) works as priority.
        """

        self.assertTrue("ARGRELAY_CONF_BASE_DIR" not in os.environ)

    @skipIf(
        os.environ.get("ARGRELAY_DEV_SHELL", False) or os.environ.get("PYCHARM_HOSTED", False),
        "To allow deployed config files, skip when in `dev_shell.bash` or in IDE.",
    )
    def test_config_files_are_not_deployed(self):
        """
        Ensure server and client config files are not deployed:

        *   `~/.argrelay.conf.d/argrelay.server.yaml`
        *   `~/.argrelay.conf.d/argrelay.client.json`

        Move them under different name to preserve or delete them completely.

        This, in turn ensures that no other tests rely on their existence (and use proper file access mocking).

        Note that `test_config_base_dir_is_not_overriden` ensures that we only need to test for ~ = user home.
        """

        for file_path in [
            os.path.expanduser("~") + "/.argrelay.conf.d/argrelay.server.yaml",
            os.path.expanduser("~") + "/.argrelay.conf.d/argrelay.client.json",
        ]:
            self.assertFalse(os.path.exists(file_path))

    # TODO: Run test-loading other than default demo data.
