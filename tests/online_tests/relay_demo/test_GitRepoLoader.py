import os
import subprocess
import tempfile
from copy import deepcopy
from unittest import TestCase

from argrelay.misc_helper import eprint
from argrelay.relay_demo.GitRepoArgType import GitRepoArgType
from argrelay.relay_demo.GitRepoLoader import GitRepoLoader
from argrelay.relay_demo.GitRepoLoaderConfigSchema import base_path_, is_plugin_enabled_
from argrelay.test_helper import line_no
from argrelay.test_helper.EnvMockBuilder import relay_demo_static_data_object


class ThisTestCase(TestCase):
    temp_dir: tempfile.TemporaryDirectory

    def clean_temp_dir(self, is_successful: bool):
        if not is_successful:
            with self.temp_dir:
                eprint(f"cleaning: {self.temp_dir.name}")
                pass

    def setUp(self):

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
        self.clean_temp_dir(False)

    def test_loader(self):
        test_cases = [
            (
                line_no(), "",
                {
                    is_plugin_enabled_: True,
                },
            ),
        ]
        static_data = deepcopy(relay_demo_static_data_object)
        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    case_comment,
                    plugin_config,
                ) = test_case

                # Temporary `base_path`:
                plugin_config[base_path_] = self.temp_dir.name

                git_repo_loader = GitRepoLoader(plugin_config)
                static_data = git_repo_loader.update_static_data(static_data)

                for type_name in [enum_item.name for enum_item in GitRepoArgType]:
                    assert type_name in static_data.known_arg_types

                    # Find list all values in data_envelope per `type_name`:
                    typed_values = []
                    for data_envelope in static_data.data_envelopes:
                        if type_name in data_envelope:
                            typed_values.append(data_envelope[type_name])
                    print(f"type_to_values: {type_name}: {typed_values}")
