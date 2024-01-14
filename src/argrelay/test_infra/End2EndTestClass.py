from __future__ import annotations

import os
import subprocess
from typing import Union

from icecream import ic

from argrelay.client_spec.ShellContext import (
    COMP_LINE_env_var,
    COMP_POINT_env_var,
    COMP_TYPE_env_var,
    COMP_KEY_env_var,
    UNKNOWN_COMP_KEY,
)
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.test_infra import parse_line_and_cpos
from argrelay.test_infra.ClientServerTestClass import ClientServerTestClass
from argrelay.test_infra.EnvMockBuilder import EmptyEnvMockBuilder, EnvMockBuilder


class End2EndTestClass(ClientServerTestClass):
    """
    Supports FS_66_17_43_42 test_infra / special test mode #5.

    In addition to starting server via its generated file in `@/bin/` dir (what `ClientServerTestClass` does),
    this tests also runs client via the generated file.

    Effectively, this runs both client and server outside the OS process responsible for running this test
    making all assertions via exit codes, stdout, stderr - what OS can provide as output of the OS process.

    It is probably "the fattest" test possible with end-to-end coverage while still using Python.
    """

    bound_command_env_var_name = "ARGRELAY_CLIENT_COMMAND"
    default_bound_command = os.environ.get(bound_command_env_var_name, "some_command")

    def env_vars(
        self,
        test_line: str,
        comp_type: CompType,
    ):
        (command_line, cursor_cpos) = parse_line_and_cpos(test_line)
        env_vars = os.environ.copy()
        env_vars[COMP_LINE_env_var] = command_line
        env_vars[COMP_POINT_env_var] = str(cursor_cpos)
        env_vars[COMP_TYPE_env_var] = str(comp_type.value)
        env_vars[COMP_KEY_env_var] = UNKNOWN_COMP_KEY
        return env_vars

    def run_client_with_cli_args(
        self,
        command_line_args,
        expected_exit_code,
    ):
        """
        See `CallConv.CliArgsConv`.
        """
        client_proc = subprocess.run(
            args = command_line_args,
            capture_output = True,
        )
        if expected_exit_code is not None:
            self.assertEqual(
                expected_exit_code,
                client_proc.returncode,
            )
        return client_proc

    def run_client_with_env_vars(
        self,
        command_name,
        env_vars,
        expected_exit_code,
    ):
        """
        See `CallConv.EnvVarsConv`.
        """
        client_proc = subprocess.run(
            args = [
                command_name,
            ],
            env = env_vars,
            capture_output = True,
        )
        if expected_exit_code is not None:
            self.assertEqual(
                expected_exit_code,
                client_proc.returncode,
            )
        return client_proc

    # TODO: allow have something on STDERR (even if it is wrong, we want this option to register known bugs to be fixed)
    def assert_no_stderr(
        self,
        stderr_str,
        server_action: ServerAction,
    ):
        self.assertEqual(
            "",
            stderr_str,
            f"{server_action} should have nothing on STDERR."
        )

    def assert_ProposeArgValues(
        self,
        command_name,
        test_line,
        comp_type: CompType,
        expected_stdout_str: Union[str, None],
        expected_exit_code = 0,
        env_mock_builder: EnvMockBuilder = None,
    ):
        if env_mock_builder is None:
            env_mock_builder = (
                EmptyEnvMockBuilder()
                .set_client_config_dict()
                .set_generate_client_config_file(True)
                .set_show_pending_spinner(False)
            )
        with env_mock_builder.build():
            assert comp_type in [
                CompType.PrefixShown,
                CompType.PrefixHidden,
                CompType.SubsequentHelp,
                CompType.MenuCompletion,
            ]
            env_vars = self.env_vars(
                test_line,
                comp_type,
            )
            client_proc = self.run_client_with_env_vars(
                command_name,
                env_vars,
                expected_exit_code,
            )
            stdout_str = client_proc.stdout.decode("utf-8")
            if expected_stdout_str is not None:
                self.assertEqual(
                    expected_stdout_str,
                    stdout_str,
                )
            stderr_str = client_proc.stderr.decode("utf-8")
            self.assert_no_stderr(
                stderr_str,
                ServerAction.ProposeArgValues,
            )
            return stdout_str

    def assert_DescribeLineArgs(
        self,
        command_name,
        test_line,
        expected_stdout_str: Union[str, None],
        expected_exit_code: Union[int, None] = 0,
        env_mock_builder: EnvMockBuilder = None,
    ):
        if env_mock_builder is None:
            env_mock_builder = (
                EmptyEnvMockBuilder()
                .set_client_config_dict()
                .set_generate_client_config_file(True)
                .set_show_pending_spinner(False)
            )
        with env_mock_builder.build():
            env_vars = self.env_vars(
                test_line,
                CompType.DescribeArgs,
            )
            client_proc = self.run_client_with_env_vars(
                command_name,
                env_vars,
                expected_exit_code,
            )
            stdout_str = client_proc.stdout.decode("utf-8")
            if expected_stdout_str is not None:
                self.assertEqual(
                    expected_stdout_str,
                    stdout_str,
                )
            stderr_str = client_proc.stderr.decode("utf-8")
            self.assert_no_stderr(
                stderr_str,
                ServerAction.ProposeArgValues,
            )
            return ic(stdout_str)

    def assert_RelayLineArgs(
        self,
        command_line_args: list[str],
        expected_stdout_str: Union[str, None],
        expected_stderr_str: Union[str, None],
        expected_exit_code: Union[int, None] = 0,
        env_mock_builder: EnvMockBuilder = None,
    ):
        if env_mock_builder is None:
            env_mock_builder = (
                EmptyEnvMockBuilder()
                .set_client_config_dict()
                .set_generate_client_config_file(True)
                .set_show_pending_spinner(False)
            )
        with env_mock_builder.build():

            client_proc = self.run_client_with_cli_args(
                command_line_args,
                expected_exit_code,
            )
            stdout_str = client_proc.stdout.decode("utf-8")
            if expected_stdout_str is not None:
                self.assertEqual(
                    expected_stdout_str,
                    stdout_str,
                )
            stderr_str = client_proc.stderr.decode("utf-8")
            if expected_stderr_str is not None:
                self.assertEqual(
                    expected_stderr_str,
                    stderr_str,
                )
