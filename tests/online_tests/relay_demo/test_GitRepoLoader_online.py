import os
import subprocess
import tempfile

from argrelay.client_command_local.ClientCommandLocal import ClientCommandLocal
from argrelay.custom_integ.GitRepoEntryConfigSchema import (
    repo_rel_path_,
    is_repo_enabled_,
    envelope_properties_,
)
from argrelay.custom_integ.GitRepoEnvelopeClass import GitRepoEnvelopeClass
from argrelay.custom_integ.GitRepoLoader import GitRepoLoader
from argrelay.custom_integ.GitRepoLoaderConfigSchema import (
    load_git_commits_default_,
    repo_entries_,
)
from argrelay.custom_integ.GitRepoPropName import GitRepoPropName
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.misc_helper_common import eprint, get_argrelay_dir
from argrelay.relay_client import __main__
from argrelay.relay_server.LocalServer import LocalServer
from argrelay.schema_config_plugin.PluginConfigSchema import plugin_config_desc, server_plugin_instances_
from argrelay.schema_config_plugin.PluginEntrySchema import plugin_config_
from argrelay.test_infra import line_no
from argrelay.test_infra.BaseTestClass import BaseTestClass
from argrelay.test_infra.EnvMockBuilder import (
    LocalClientEnvMockBuilder,
)


class ThisTestClass(BaseTestClass):
    temp_dir: tempfile.TemporaryDirectory

    def clean_temp_dir(self, is_successful: bool):
        if not is_successful:
            with self.temp_dir:
                eprint(f"cleaning up: {self.temp_dir.name}")

    def setUp(self):
        super().setUp()

        base_tmp_dir = f"{get_argrelay_dir()}/tmp"
        assert os.path.isdir(base_tmp_dir)

        test_configs_dir = f"{base_tmp_dir}/test_data"
        if not os.path.exists(test_configs_dir):
            os.makedirs(test_configs_dir)

        self.temp_dir = tempfile.TemporaryDirectory(dir = f"{test_configs_dir}/")

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
                line_no(), f"`{GitRepoLoader.__name__}.default` enabled with random temp dir",
                {
                    load_git_commits_default_: True,
                    repo_entries_: {
                        self.temp_dir.name: [
                            {
                                repo_rel_path_: "qwer/abc",
                                envelope_properties_: {
                                    GitRepoPropName.git_repo_alias.name: "ar",
                                    GitRepoPropName.git_repo_content_type.name: "self",
                                },
                            },
                            {
                                repo_rel_path_: "qwer/xyz",
                                is_repo_enabled_: True,
                                envelope_properties_: {
                                    GitRepoPropName.git_repo_alias.name: "ac",
                                    GitRepoPropName.git_repo_content_type.name: "code",
                                },
                            },
                            {
                                repo_rel_path_: "zxcv",
                                is_repo_enabled_: True,
                                envelope_properties_: {
                                    GitRepoPropName.git_repo_alias.name: "clone",
                                    GitRepoPropName.git_repo_content_type.name: "self",
                                },
                            },
                            {
                                repo_rel_path_: "poiu",
                                is_repo_enabled_: False,
                                envelope_properties_: {
                                    GitRepoPropName.git_repo_alias.name: "missing",
                                    GitRepoPropName.git_repo_content_type.name: "conf",
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
                plugin_config_dict = plugin_config_desc.dict_from_default_file()
                plugin_config_dict[server_plugin_instances_][
                    f"{GitRepoLoader.__name__}.default"
                ][plugin_config_] = plugin_config

                env_mock_builder = (
                    LocalClientEnvMockBuilder()
                    .set_plugin_config_dict(plugin_config_dict)
                    .set_enable_demo_git_loader(True)
                    .set_command_line("some_command help")
                    .set_cursor_cpos(0)
                    .set_comp_type(CompType.PrefixShown)
                )
                with env_mock_builder.build():
                    # The test simply triggers server data load and verifies its loaded.

                    # Populate static data by plugin via `ClientLocal` who starts `LocalServer`:
                    command_obj: ClientCommandLocal = __main__.main()
                    assert isinstance(command_obj, ClientCommandLocal)
                    local_server: LocalServer = command_obj.local_server

                    repo_envelopes = local_server.query_engine.query_data_envelopes(
                        GitRepoEnvelopeClass.class_git_repo.name,
                        {
                            f"{ReservedPropName.envelope_class.name}": f"{GitRepoEnvelopeClass.class_git_repo.name}",
                        },
                    )

                    # Verify:
                    are_all_empty = True
                    for type_name in [enum_item.name for enum_item in GitRepoPropName]:
                        # Find list of all values in `data_envelope`-s per `type_name`:
                        typed_values = []
                        for data_envelope in repo_envelopes:
                            if type_name in data_envelope:
                                typed_value = data_envelope[type_name]
                                if typed_value not in typed_values:
                                    typed_values.append(typed_value)
                        if len(typed_values) != 0:
                            are_all_empty = False
                        print(f"type_to_values: {type_name}: {typed_values}")
                    assert not are_all_empty
