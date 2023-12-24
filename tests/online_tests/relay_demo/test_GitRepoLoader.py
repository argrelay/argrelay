import os
import subprocess
import tempfile

from argrelay.client_command_local.AbstractLocalClientCommand import AbstractLocalClientCommand
from argrelay.custom_integ.GitRepoArgType import GitRepoArgType
from argrelay.custom_integ.GitRepoEntryConfigSchema import (
    repo_rel_path_,
    is_repo_enabled_,
    envelope_properties_,
)
from argrelay.custom_integ.GitRepoLoader import GitRepoLoader
from argrelay.custom_integ.GitRepoLoaderConfigSchema import (
    load_repo_commits_,
    repo_entries_,
)
from argrelay.misc_helper_common import eprint
from argrelay.relay_client import __main__
from argrelay.schema_config_core_server.ServerConfigSchema import plugin_instance_entries_
from argrelay.schema_config_plugin.PluginEntrySchema import plugin_config_
from argrelay.test_infra import line_no
from argrelay.test_infra.BaseTestClass import BaseTestClass
from argrelay.test_infra.EnvMockBuilder import (
    load_custom_integ_server_config_dict,
    LocalClientEnvMockBuilder,
)


class ThisTestClass(BaseTestClass):
    temp_dir: tempfile.TemporaryDirectory

    def clean_temp_dir(self, is_successful: bool):
        if not is_successful:
            with self.temp_dir:
                eprint(f"cleaning: {self.temp_dir.name}")
                pass

    def setUp(self):
        super().setUp()

        self.temp_dir = tempfile.TemporaryDirectory()
        is_successful = False
        try:
            # checkout repos under temp_dir:
            for repo_item in [
                {
                    "git_root_path": "qwer/abc",
                    "git_remote_url": "git@github.com:uvsmtid/argrelay.git",
                },
                {
                    "git_root_path": "qwer/xyz",
                    "git_remote_url": "git@github.com:kislyuk/argcomplete.git",
                },
                {
                    "git_root_path": "zxcv",
                    "git_remote_url": "git@github.com:uvsmtid/argrelay.git",
                },
            ]:
                repo_path = os.path.join(self.temp_dir.name, repo_item["git_root_path"])
                repo_url = repo_item["git_remote_url"]
                print(f"clone from \"{repo_url}\" into \"{repo_path}\"")
                subprocess.check_output(
                    [
                        "git",
                        "clone",
                        repo_url,
                        repo_path,
                    ]
                )

            # all repo clones succeeded - disable deletion:
            is_successful = True

        finally:
            self.clean_temp_dir(is_successful)

    def tearDown(self):
        super().tearDown()
        self.clean_temp_dir(False)

    def test_loader(self):
        test_cases = [
            (
                line_no(), f"{GitRepoLoader.__name__} enabled with random temp dir",
                {
                    load_repo_commits_: True,
                    repo_entries_: {
                        self.temp_dir.name: [
                            {
                                repo_rel_path_: "qwer/abc",
                                envelope_properties_: {
                                    GitRepoArgType.GitRepoAlias.name: "ar",
                                    GitRepoArgType.GitRepoContentType.name: "self",
                                },
                            },
                            {
                                repo_rel_path_: "qwer/xyz",
                                is_repo_enabled_: True,
                                envelope_properties_: {
                                    GitRepoArgType.GitRepoAlias.name: "ac",
                                    GitRepoArgType.GitRepoContentType.name: "code",
                                },
                            },
                            {
                                repo_rel_path_: "zxcv",
                                is_repo_enabled_: True,
                                envelope_properties_: {
                                    GitRepoArgType.GitRepoAlias.name: "clone",
                                    GitRepoArgType.GitRepoContentType.name: "self",
                                },
                            },
                            {
                                repo_rel_path_: "poiu",
                                is_repo_enabled_: False,
                                envelope_properties_: {
                                    GitRepoArgType.GitRepoAlias.name: "missing",
                                    GitRepoArgType.GitRepoContentType.name: "conf",
                                },
                            },
                        ],
                    },
                },
            ),
        ]
        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    case_comment,
                    plugin_config,
                ) = test_case

                # Modify config to enable `GitRepoLoader` plugin:
                server_config_dict = load_custom_integ_server_config_dict()
                server_config_dict[plugin_instance_entries_][GitRepoLoader.__name__][plugin_config_] = plugin_config

                env_mock_builder = (
                    LocalClientEnvMockBuilder()
                    .set_server_config_dict(server_config_dict)
                    .set_enable_demo_git_loader(True)
                    .set_command_line("some_command help")
                    .set_cursor_cpos(0)
                )
                with env_mock_builder.build():
                    # Populate static data by plugin via `LocalClient` who starts `LocalServer`:
                    command_obj: AbstractLocalClientCommand = __main__.main()
                    assert isinstance(command_obj, AbstractLocalClientCommand)
                    static_data = command_obj.local_server.server_config.static_data

                    # Verify:
                    for type_name in [enum_item.name for enum_item in GitRepoArgType]:
                        assert type_name in static_data.known_arg_types

                        # Find list of all values in `data_envelope` per `type_name`:
                        typed_values = []
                        for data_envelope in static_data.data_envelopes:
                            if type_name in data_envelope:
                                typed_values.append(data_envelope[type_name])
                        print(f"type_to_values: {type_name}: {typed_values}")
