import subprocess
from subprocess import CalledProcessError

from argrelay.test_infra import line_no, change_to_known_repo_path
from argrelay.test_infra.BaseTestClass import BaseTestClass
from argrelay.test_infra.EnvMockBuilder import mock_subprocess_popen


class ThisTestClass(BaseTestClass):
    """
    Test assumptions that `PopenMock` works as expected.
    """

    def test_PopenMock_via_Open_by_pass(self):
        """
        This test uses `PopenMock` config with `None` values to bypass mock and actually call external command.

        Hope the output of chosen commands does not depend on the target machine (at least by asserted values).
        """

        # @formatter:off
        test_cases = [
            (
                line_no(),
                {
                    ("true", ): None,
                },
                lambda: subprocess.run(
                    ["true"],
                    capture_output = True,
                ),
                (
                    ["true"], 0, b"", b"",
                ),
                "Execute (basic) real external command successfully",
            ),
            (
                line_no(),
                {
                    ("false", ): None,
                },
                lambda: subprocess.run(
                    ["false"],
                    capture_output = True,
                ),
                (
                    ["false"], 1, b"", b"",
                ),
                "Execute (basic) real external command unsuccessfully",
            ),
            (
                line_no(),
                {
                    ("ls",): (0, "some ls stdout", "some ls stderr",),
                    ("ls", "-1", "../exe"): None,
                },
                lambda: subprocess.run(
                    ["ls", "-1", "../exe"],
                    capture_output = True,
                ),
                (
                    ["ls", "-1", "../exe"],
                    0,
                    b"""argrelay_common_lib.bash
argrelay_rc.bash
bootstrap_dev_env.bash
build_project.bash
deploy_config_files_conf.bash
deploy_project.bash
deploy_resource_files_conf.bash
dev_shell.bash
init_shell_env.bash
play_x_server_demo.bash
publish_package.bash
relay_demo.bash
run_argrelay_client
run_argrelay_server
run_max_tests.bash
squash_branch.bash
upgrade_all_packages.bash
""",
                    b"",
                ),
                "Execute (more complex) real external command successfully",
            ),
            (
                line_no(),
                {
                    ("ls",): (0, "some ls stdout", "some ls stderr",),
                    ("ls", "-1", "missing_dir_entry",): None,
                },
                lambda: subprocess.run(
                    ["ls", "-1", "missing_dir_entry",],
                    # Not capturing output (stderr may vary a lot depending on the target machine).
                ),
                (
                    ["ls", "-1", "missing_dir_entry"],
                    2,
                    None,
                    None,
                ),
                "Execute (more complex) real external command unsuccessfully",
            ),
        ]
        # @formatter:on

        with change_to_known_repo_path("./tests"):
            for test_case in test_cases:
                with self.subTest(test_case):
                    (
                        line_number,
                        expected_args_to_output,
                        popen_interaction,
                        popen_expected_output,
                        case_comment,
                    ) = test_case

                    with mock_subprocess_popen(expected_args_to_output) as popen_mock:
                        sub_proc = popen_interaction()
                        self.assertEqual(
                            (
                                sub_proc.args,
                                sub_proc.returncode,
                                sub_proc.stdout,
                                sub_proc.stderr,
                            ),
                            popen_expected_output,
                        )

    def test_PopenMock_via_run_and_direct_Popen(self):

        # @formatter:off
        test_cases = [
            (
                line_no(),
                {
                    ("ls",): (0, "some ls stdout", "some ls stderr",),
                },
                lambda: subprocess.run(
                    ["ls"],
                ),
                (
                    ["ls"], 0, "some ls stdout", "some ls stderr",
                ),
                None,
                "Basic call to `subprocess.run(...)` to succeed because of matching CLI.",
            ),
            (
                line_no(),
                {
                    ("ls",): (0, "some ls stdout", "some ls stderr",),
                },
                lambda: subprocess.run(
                    ["ls", "-lrt"],
                ),
                None,
                f"unexpected CLI args: `['ls', '-lrt']` expected CLI args: `dict_keys([('ls',)])`",
                "Basic call to `subprocess.run(...)` to fail because of non-matching CLI.",
            ),
            (
                line_no(),
                {
                    "~/argrelay.git/tmp/mongo/mongodb-linux-x86_64-rhel80-6.0.3/bin/mongod --dbpath ~/argrelay.git/tmp/mongo/data": (
                        0,
                        "MongoDB start stdout",
                        "MongoDB start stdout",
                    ),
                },
                lambda: subprocess.Popen(
                "~/argrelay.git/tmp/mongo/mongodb-linux-x86_64-rhel80-6.0.3/bin/mongod --dbpath ~/argrelay.git/tmp/mongo/data",
                    shell = True,
                ),
                (
                    "~/argrelay.git/tmp/mongo/mongodb-linux-x86_64-rhel80-6.0.3/bin/mongod --dbpath ~/argrelay.git/tmp/mongo/data",
                    0,
                    "MongoDB start stdout",
                    "MongoDB start stdout",
                ),
                None,
                "Direct call to `Popen` with `shell = True` to succeed for starting MongoDB based on server config.",
            ),
            (
                line_no(),
                {
                    ("ls", "-lrt", "1",): (0, "1 stdout", "1 stderr",),
                    ("ls", "-lrt", "2",): (0, "2 stdout", "2 stderr",),
                },
                lambda: subprocess.run(
                    ["ls", "-lrt", "1"],
                ),
                (
                    ["ls", "-lrt", "1"], 0, "1 stdout", "1 stderr",
                ),
                None,
                "Basic call to `subprocess.run(...)` multiple expected input to succeed because of matching CLI 1.",
            ),
            (
                line_no(),
                {
                    ("ls", "-lrt", "1",): (0, "1 stdout", "1 stderr",),
                    ("ls", "-lrt", "2",): (0, "2 stdout", "2 stderr",),
                },
                lambda: subprocess.run(
                    ["ls", "-lrt", "2"],
                ),
                (
                    ["ls", "-lrt", "2"], 0, "2 stdout", "2 stderr",
                ),
                None,
                "Basic call to `subprocess.run(...)` multiple expected input to succeed because of matching CLI 2.",
            ),
            (
                line_no(),
                {
                    ("ls", "-lrt", "1",): (0, "1 stdout", "1 stderr",),
                    ("ls", "-lrt", "2",): (0, "2 stdout", "2 stderr",),
                },
                lambda: subprocess.run(
                    ["ls", "-lrt", "3"],
                ),
                None,
                f"unexpected CLI args: `['ls', '-lrt', '3']` expected CLI args: `dict_keys([('ls', '-lrt', '1'), ('ls', '-lrt', '2')])`",
                "Basic call to `subprocess.run(...)` multiple expected input to succeed because of non-matching CLI 3.",
            ),
        ]
        # @formatter:on

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    expected_args_to_output,
                    popen_interaction,
                    popen_expected_output,
                    expected_exception,
                    case_comment,
                ) = test_case

                with mock_subprocess_popen(expected_args_to_output) as popen_mock:
                    if not expected_exception:
                        sub_proc = popen_interaction()
                        self.assertEqual(
                            (
                                sub_proc.args,
                                sub_proc.returncode,
                                sub_proc.stdout,
                                sub_proc.stderr,
                            ),
                            popen_expected_output,
                        )
                    else:
                        self.assertIsNone(
                            popen_expected_output,
                            self.confusing_result_presence_msg,
                        )
                        with self.assertRaises(ValueError) as exc_context:
                            sub_proc = popen_interaction()
                        self.assertEqual(
                            expected_exception,
                            exc_context.exception.args[0],
                        )

    def test_PopenMock_via_call(self):

        # @formatter:off
        test_cases = [
            (
                line_no(),
                {
                    ("ls",): (0, "some ls stdout", "some ls stderr",),
                },
                lambda: subprocess.call(
                    ["ls"],
                ),
                (
                    ["ls"], 0, "some ls stdout", "some ls stderr",
                ),
                None,
                "Basic call to `subprocess.call(...)` to succeed because of matching CLI: 0 exit code.",
            ),
            (
                line_no(),
                {
                    ("ls",): (1, "some ls stdout", "some ls stderr",),
                },
                lambda: subprocess.call(
                    ["ls"],
                ),
                (
                    ["ls"], 1, "some ls stdout", "some ls stderr",
                ),
                None,
                "Basic call to `subprocess.call(...)` to succeed because of matching CLI: 1 exit code.",
            ),
        ]
        # @formatter:on

        for test_case in test_cases:
            with self.subTest(test_case):
                (
                    line_number,
                    expected_args_to_output,
                    popen_interaction,
                    popen_expected_output,
                    expected_exception,
                    case_comment,
                ) = test_case

                with mock_subprocess_popen(expected_args_to_output) as popen_mock:
                    if not expected_exception:
                        exit_code = popen_interaction()
                        self.assertEqual(
                            exit_code,
                            popen_expected_output[1],
                        )
                    else:
                        self.assertIsNone(
                            popen_expected_output,
                            self.confusing_result_presence_msg,
                        )
                        with self.assertRaises(ValueError) as exc_context:
                            exit_code = popen_interaction()
                        self.assertEqual(
                            expected_exception,
                            exc_context.exception.args[0],
                        )

    def test_PopenMock_via_check_call_with_0_exit_code(self):

        expected_args_to_output = {
            ("ls",): (0, "some ls stdout", "some ls stderr",),
        }

        with mock_subprocess_popen(expected_args_to_output) as popen_mock:
            exit_code = subprocess.check_call(["ls"])

            self.assertEqual(
                exit_code,
                0,
            )

    def test_PopenMock_via_check_call_with_1_exit_code(self):

        expected_args_to_output = {
            ("ls",): (1, "some ls stdout", "some ls stderr",),
        }

        with mock_subprocess_popen(expected_args_to_output) as popen_mock:
            with self.assertRaises(CalledProcessError) as exc_context:
                exit_code = subprocess.check_call(["ls"])
                assert exit_code != 0, "unreachable but true"

            self.assertEqual(
                1,
                exc_context.exception.args[0],
                "exit code",
            )
            self.assertEqual(
                ["ls"],
                exc_context.exception.args[1],
                "CLI args",
            )
