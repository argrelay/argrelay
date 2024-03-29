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
from argrelay.custom_integ.GitRepoEnvelopeClass import GitRepoEnvelopeClass
from argrelay.custom_integ.GitRepoLoader import GitRepoLoader
from argrelay.custom_integ.GitRepoLoaderConfigSchema import (
    load_git_commits_default_,
    repo_entries_,
)
from argrelay.enum_desc.CompType import CompType
from argrelay.misc_helper_common import eprint, get_argrelay_dir
from argrelay.relay_client import __main__
from argrelay.runtime_data.EnvelopeCollection import EnvelopeCollection
from argrelay.schema_config_core_server.ServerConfigSchema import plugin_instance_entries_, server_config_desc
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
                                    GitRepoArgType.git_repo_alias.name: "ar",
                                    GitRepoArgType.git_repo_content_type.name: "self",
                                },
                            },
                            {
                                repo_rel_path_: "qwer/xyz",
                                is_repo_enabled_: True,
                                envelope_properties_: {
                                    GitRepoArgType.git_repo_alias.name: "ac",
                                    GitRepoArgType.git_repo_content_type.name: "code",
                                },
                            },
                            {
                                repo_rel_path_: "zxcv",
                                is_repo_enabled_: True,
                                envelope_properties_: {
                                    GitRepoArgType.git_repo_alias.name: "clone",
                                    GitRepoArgType.git_repo_content_type.name: "self",
                                },
                            },
                            {
                                repo_rel_path_: "poiu",
                                is_repo_enabled_: False,
                                envelope_properties_: {
                                    GitRepoArgType.git_repo_alias.name: "missing",
                                    GitRepoArgType.git_repo_content_type.name: "conf",
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
                server_config_dict = server_config_desc.dict_from_default_file()
                server_config_dict[plugin_instance_entries_][
                    f"{GitRepoLoader.__name__}.default"
                ][plugin_config_] = plugin_config

                env_mock_builder = (
                    LocalClientEnvMockBuilder()
                    .set_server_config_dict(server_config_dict)
                    .set_enable_demo_git_loader(True)
                    .set_command_line("some_command help")
                    .set_cursor_cpos(0)
                    .set_comp_type(CompType.PrefixShown)
                )
                with env_mock_builder.build():
                    # The test simply triggers server data load and verifies its loaded.

                    # Populate static data by plugin via `LocalClient` who starts `LocalServer`:
                    command_obj: AbstractLocalClientCommand = __main__.main()
                    assert isinstance(command_obj, AbstractLocalClientCommand)
                    static_data = command_obj.local_server.server_config.static_data

                    repo_envelope_collection = static_data.envelope_collections.setdefault(
                        GitRepoEnvelopeClass.ClassGitRepo.name,
                        EnvelopeCollection(
                            index_fields = [],
                            data_envelopes = [],
                        ),
                    )

                    # Verify:
                    are_all_empty = True
                    for type_name in [enum_item.name for enum_item in GitRepoArgType]:
                        assert type_name in static_data.envelope_collections[
                            GitRepoEnvelopeClass.ClassGitRepo.name
                        ].index_fields

                        # Find list of all values in `data_envelope`-s per `type_name`:
                        typed_values = []
                        for data_envelope in repo_envelope_collection.data_envelopes:
                            if type_name in data_envelope:
                                typed_value = data_envelope[type_name]
                                if typed_value not in typed_values:
                                    typed_values.append(typed_value)
                        if len(typed_values) != 0:
                            are_all_empty = False
                        print(f"type_to_values: {type_name}: {typed_values}")
                    assert not are_all_empty
