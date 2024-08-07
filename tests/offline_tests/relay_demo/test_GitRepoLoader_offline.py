from argrelay.client_command_local.ClientCommandLocal import ClientCommandLocal
from argrelay.custom_integ.GitRepoEntryConfigSchema import (
    repo_rel_path_,
    envelope_properties_,
    load_tags_last_days_,
    load_commits_max_count_,
)
from argrelay.custom_integ.GitRepoEnvelopeClass import GitRepoEnvelopeClass
from argrelay.custom_integ.GitRepoLoader import GitRepoLoader
from argrelay.custom_integ.GitRepoLoaderConfigSchema import (
    load_git_commits_default_,
    repo_entries_,
    load_git_tags_default_,
)
from argrelay.custom_integ.GitRepoPropName import GitRepoPropName
from argrelay.enum_desc.CompType import CompType
from argrelay.misc_helper_common import get_argrelay_dir
from argrelay.relay_client import __main__
from argrelay.runtime_data.EnvelopeCollection import EnvelopeCollection
from argrelay.schema_config_plugin.PluginConfigSchema import plugin_config_desc, plugin_instance_entries_
from argrelay.schema_config_plugin.PluginEntrySchema import (
    plugin_enabled_,
    plugin_dependencies_,
    plugin_config_,
)
from argrelay.test_infra import line_no
from argrelay.test_infra.EnvMockBuilder import (
    LocalClientEnvMockBuilder,
)
from argrelay.test_infra.LocalTestClass import LocalTestClass


class ThisTestClass(LocalTestClass):
    """
    Tests FS_67_16_61_97 git plugin
    """

    same_test_data_per_class = "TD_70_69_38_46"  # no data

    def test_loader(self):

        git_loader_plugin_instance_id = f"{GitRepoLoader.__name__}.self"
        argrelay_git_repo_dir = get_argrelay_dir()

        test_cases = [
            (
                line_no(),
                f"`{git_loader_plugin_instance_id}` with empty base path and empty rel path (to load local argrelay.git)",
                {
                    repo_entries_: {
                        "": [
                            {
                                repo_rel_path_: "",
                                envelope_properties_: {
                                    GitRepoPropName.git_repo_alias.name: "ar",
                                    GitRepoPropName.git_repo_content_type.name: "self",
                                },
                            },
                        ],
                    },
                },
                {
                }
            ),
            (
                line_no(),
                f"`{git_loader_plugin_instance_id}` with empty base path and non-empty rel path (to load local argrelay.git)",
                {
                    repo_entries_: {
                        "/": [
                            {
                                repo_rel_path_: argrelay_git_repo_dir,
                                envelope_properties_: {
                                    GitRepoPropName.git_repo_alias.name: "ar",
                                    GitRepoPropName.git_repo_content_type.name: "self",
                                },
                            },
                        ],
                    },
                },
                {
                }
            ),
            (
                line_no(),
                f"`{git_loader_plugin_instance_id}` with non-empty base path and empty rel path (to load local argrelay.git)",
                {
                    repo_entries_: {
                        argrelay_git_repo_dir: [
                            {
                                repo_rel_path_: "",
                                envelope_properties_: {
                                    GitRepoPropName.git_repo_alias.name: "ar",
                                    GitRepoPropName.git_repo_content_type.name: "self",
                                },
                            },
                        ],
                    },
                },
                {
                }
            ),
            (
                line_no(),
                f"`{git_loader_plugin_instance_id}` loads repo without tags and commits",
                {
                    load_git_tags_default_: False,
                    load_git_commits_default_: False,
                    repo_entries_: {
                        "": [
                            {
                                repo_rel_path_: "",
                                envelope_properties_: {
                                    GitRepoPropName.git_repo_alias.name: "ar",
                                    GitRepoPropName.git_repo_content_type.name: "self",
                                },
                            },
                        ],
                    },
                },
                {
                    GitRepoEnvelopeClass.ClassGitRepo.name: {
                        GitRepoPropName.git_repo_object_category.name: True,
                        # Expect all repo-related metadata for `GitRepoEnvelopeClass.ClassGitRepo`:
                        GitRepoPropName.git_repo_alias.name: True,
                        GitRepoPropName.git_repo_root_abs_path.name: True,
                        GitRepoPropName.git_repo_root_rel_path.name: True,
                        GitRepoPropName.git_repo_root_base_name.name: True,
                        GitRepoPropName.git_repo_content_type.name: True,
                        # Commit-related metadata should not be seen for `GitRepoEnvelopeClass.ClassGitRepo`:
                        GitRepoPropName.git_repo_commit_id.name: False,
                        GitRepoPropName.git_repo_short_commit_id.name: False,
                        GitRepoPropName.git_repo_commit_message.name: False,
                        GitRepoPropName.git_repo_commit_author_name.name: False,
                        GitRepoPropName.git_repo_commit_author_email.name: False,
                    },
                    GitRepoEnvelopeClass.ClassGitTag.name: {
                        GitRepoPropName.git_repo_object_category.name: False,
                        # Tag-related metadata should not be as loading commits is disabled:
                        GitRepoPropName.git_repo_tag_name.name: False,
                        GitRepoPropName.git_repo_commit_id.name: False,
                        GitRepoPropName.git_repo_short_commit_id.name: False,
                        GitRepoPropName.git_repo_commit_message.name: False,
                        GitRepoPropName.git_repo_commit_author_name.name: False,
                        GitRepoPropName.git_repo_commit_author_email.name: False,
                    },
                    GitRepoEnvelopeClass.ClassGitCommit.name: {
                        GitRepoPropName.git_repo_object_category.name: False,
                        # Commit-related metadata should not be as loading commits is disabled:
                        GitRepoPropName.git_repo_commit_id.name: False,
                        GitRepoPropName.git_repo_short_commit_id.name: False,
                        GitRepoPropName.git_repo_commit_message.name: False,
                        GitRepoPropName.git_repo_commit_author_name.name: False,
                        GitRepoPropName.git_repo_commit_author_email.name: False,
                    },
                }
            ),
            (
                line_no(),
                f"`{git_loader_plugin_instance_id}` loads repo with tags but without commits",
                {
                    load_git_tags_default_: True,
                    load_git_commits_default_: False,
                    repo_entries_: {
                        "/": [
                            {
                                repo_rel_path_: argrelay_git_repo_dir,
                                load_tags_last_days_: 1000,
                                envelope_properties_: {
                                    GitRepoPropName.git_repo_alias.name: "ar",
                                    GitRepoPropName.git_repo_content_type.name: "self",
                                },
                            },
                        ],
                    },
                },
                {
                    GitRepoEnvelopeClass.ClassGitRepo.name: {
                        GitRepoPropName.git_repo_object_category.name: True,
                        # Expect all repo-related metadata for `GitRepoEnvelopeClass.ClassGitRepo`:
                        GitRepoPropName.git_repo_alias.name: True,
                        GitRepoPropName.git_repo_root_abs_path.name: True,
                        GitRepoPropName.git_repo_root_rel_path.name: True,
                        GitRepoPropName.git_repo_root_base_name.name: True,
                        GitRepoPropName.git_repo_content_type.name: True,
                        # Commit-related metadata should not be seen for `GitRepoEnvelopeClass.ClassGitRepo`:
                        GitRepoPropName.git_repo_commit_id.name: False,
                        GitRepoPropName.git_repo_short_commit_id.name: False,
                        GitRepoPropName.git_repo_commit_message.name: False,
                        GitRepoPropName.git_repo_commit_author_name.name: False,
                        GitRepoPropName.git_repo_commit_author_email.name: False,
                    },
                    GitRepoEnvelopeClass.ClassGitTag.name: {
                        GitRepoPropName.git_repo_object_category.name: True,
                        # Tag-related metadata should not be as loading commits is disabled:
                        GitRepoPropName.git_repo_tag_name.name: True,
                        GitRepoPropName.git_repo_commit_id.name: True,
                        GitRepoPropName.git_repo_short_commit_id.name: True,
                        GitRepoPropName.git_repo_commit_message.name: True,
                        GitRepoPropName.git_repo_commit_author_name.name: True,
                        GitRepoPropName.git_repo_commit_author_email.name: True,
                    },
                    GitRepoEnvelopeClass.ClassGitCommit.name: {
                        GitRepoPropName.git_repo_object_category.name: False,
                        # Commit-related metadata should not be as loading commits is disabled:
                        GitRepoPropName.git_repo_commit_id.name: False,
                        GitRepoPropName.git_repo_short_commit_id.name: False,
                        GitRepoPropName.git_repo_commit_message.name: False,
                        GitRepoPropName.git_repo_commit_author_name.name: False,
                        GitRepoPropName.git_repo_commit_author_email.name: False,
                    },
                }
            ),
            (
                line_no(),
                f"`{git_loader_plugin_instance_id}` loads repo without tags but with commits",
                {
                    load_git_tags_default_: False,
                    load_git_commits_default_: True,
                    repo_entries_: {
                        argrelay_git_repo_dir: [
                            {
                                repo_rel_path_: "",
                                load_commits_max_count_: 10,
                                envelope_properties_: {
                                    GitRepoPropName.git_repo_alias.name: "ar",
                                    GitRepoPropName.git_repo_content_type.name: "self",
                                },
                            },
                        ],
                    },
                },
                {
                    GitRepoEnvelopeClass.ClassGitRepo.name: {
                        GitRepoPropName.git_repo_object_category.name: True,
                        # Expect all repo-related metadata for `GitRepoEnvelopeClass.ClassGitRepo`:
                        GitRepoPropName.git_repo_alias.name: True,
                        GitRepoPropName.git_repo_root_abs_path.name: True,
                        GitRepoPropName.git_repo_root_rel_path.name: True,
                        GitRepoPropName.git_repo_root_base_name.name: True,
                        GitRepoPropName.git_repo_content_type.name: True,
                        # Commit-related metadata should not be seen for `GitRepoEnvelopeClass.ClassGitRepo`:
                        GitRepoPropName.git_repo_commit_id.name: False,
                        GitRepoPropName.git_repo_short_commit_id.name: False,
                        GitRepoPropName.git_repo_commit_message.name: False,
                        GitRepoPropName.git_repo_commit_author_name.name: False,
                        GitRepoPropName.git_repo_commit_author_email.name: False,
                    },
                    GitRepoEnvelopeClass.ClassGitTag.name: {
                        GitRepoPropName.git_repo_object_category.name: False,
                        # Tag-related metadata should not be as loading commits is disabled:
                        GitRepoPropName.git_repo_tag_name.name: False,
                        GitRepoPropName.git_repo_commit_id.name: False,
                        GitRepoPropName.git_repo_short_commit_id.name: False,
                        GitRepoPropName.git_repo_commit_message.name: False,
                        GitRepoPropName.git_repo_commit_author_name.name: False,
                        GitRepoPropName.git_repo_commit_author_email.name: False,
                    },
                    GitRepoEnvelopeClass.ClassGitCommit.name: {
                        GitRepoPropName.git_repo_object_category.name: True,
                        # Repo-related (parent) data:
                        GitRepoPropName.git_repo_alias.name: True,
                        GitRepoPropName.git_repo_root_abs_path.name: True,
                        GitRepoPropName.git_repo_root_rel_path.name: True,
                        GitRepoPropName.git_repo_root_base_name.name: True,
                        GitRepoPropName.git_repo_content_type.name: True,
                        # Commit-specific data:
                        GitRepoPropName.git_repo_commit_id.name: True,
                        GitRepoPropName.git_repo_short_commit_id.name: True,
                        GitRepoPropName.git_repo_commit_message.name: True,
                        GitRepoPropName.git_repo_commit_author_name.name: True,
                        GitRepoPropName.git_repo_commit_author_email.name: True,
                    },
                }
            ),
        ]
        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    case_comment,
                    plugin_config,
                    expected_non_empty_props_per_class,
                ) = test_case

                # Make `GitRepoLoader` plugin depend on all other plugins (to make it the last):
                plugin_config_dict = plugin_config_desc.dict_from_default_file()
                all_plugin_instance_ids = []
                for plugin_instance_id, plugin_instance_entry in plugin_config_dict[plugin_instance_entries_].items():
                    if git_loader_plugin_instance_id != plugin_instance_id:
                        all_plugin_instance_ids.append(plugin_instance_id)
                # Modify config to enable `GitRepoLoader` plugin:
                git_loader_plugin_instance_entry = plugin_config_dict[plugin_instance_entries_][
                    git_loader_plugin_instance_id
                ]
                git_loader_plugin_instance_entry[plugin_config_] = plugin_config
                git_loader_plugin_instance_entry[plugin_enabled_] = True
                git_loader_plugin_instance_entry[plugin_dependencies_] = all_plugin_instance_ids

                env_mock_builder = (
                    LocalClientEnvMockBuilder()
                    .set_plugin_config_dict(plugin_config_dict)
                    .set_command_line("some_command help")
                    .set_cursor_cpos(0)
                    .set_comp_type(CompType.PrefixShown)
                )
                with env_mock_builder.build():
                    # The test simply triggers server data load and verifies its loaded.

                    # Populate static data by plugin via `ClientLocal` who starts `LocalServer`:
                    command_obj: ClientCommandLocal = __main__.main()
                    assert isinstance(command_obj, ClientCommandLocal)
                    static_data = command_obj.local_server.server_config.static_data

                    # Verify:
                    for class_name, prop_name_existence_dict in expected_non_empty_props_per_class.items():

                        envelope_collection = static_data.envelope_collections.setdefault(
                            class_name,
                            EnvelopeCollection(
                                index_props = [],
                                data_envelopes = [],
                            ),
                        )

                        for prop_name, prop_name_existence in prop_name_existence_dict.items():

                            is_empty = False
                            if prop_name_existence:
                                assert prop_name in static_data.envelope_collections[class_name].index_props
                            else:
                                # Do not assert it as loader over-specifies index fields at the moment:
                                # noinspection PyUnreachableCode
                                if False:
                                    assert prop_name not in static_data.envelope_collections[class_name].index_props

                            # Find list of all values in `data_envelope`-s per `prop_name`:
                            prop_values = []
                            for data_envelope in envelope_collection.data_envelopes:
                                if prop_name in data_envelope:
                                    prop_value = data_envelope[prop_name]
                                    if prop_value not in prop_values:
                                        prop_values.append(prop_value)

                            if len(prop_values) == 0:
                                is_empty = True
                            print(f"prop_name_to_prop_values: {prop_name}: {prop_values}")

                            if prop_name_existence:
                                assert not is_empty
                            else:
                                assert is_empty
