import os
import signal
import socket
import subprocess
import time
from contextlib import closing
from unittest import TestCase, skipIf

from argrelay.client_spec.ShellContext import (
    COMP_LINE_env_var,
    COMP_POINT_env_var,
    COMP_TYPE_env_var,
    COMP_KEY_env_var,
    UNKNOWN_COMP_KEY,
)
from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.TermColor import TermColor
from argrelay.handler_response.DescribeLineArgsClientResponseHandler import indent_size
from argrelay.misc_helper import get_argrelay_dir, eprint
from argrelay.runtime_data.ClientConfig import ClientConfig
from argrelay.schema_config_core_client.ClientConfigSchema import client_config_desc
from argrelay.test_helper import change_to_known_repo_path, parse_line_and_cpos

client_command_env_var_name_ = "ARGRELAY_CLIENT_COMMAND"


@skipIf(
    (
        (not os.environ.get("ARGRELAY_DEV_SHELL", False))
        or
        (not os.environ.get("ARGRELAY_BOOTSTRAP_DEV_ENV", False))
    ),
    """
    Only `@/exe/dev_shell.bash` controllably puts `${ARGRELAY_CLIENT_COMMAND}` into `PATH` env var.
    Skip test otherwise.
    """,
)
class ThisTestCase(TestCase):
    """
    It tests both client and server started via their generated files in `@/bin/` dir.

    The test starts background server process to execute the client.

    It is probably "the fattest" test possible with end-to-end coverage while still using Python.
    """

    server_proc = None

    def setUp(self):
        # Function "desc_host" ("desc host") uses `NoopDelegator`, so the test should always pass:
        self.server_proc = subprocess.Popen([
            f"{get_argrelay_dir()}/bin/run_argrelay_server",
        ])
        self.wait_for_connection_to_server()

    def tearDown(self):
        # shutdown gracefully:
        self.server_proc.send_signal(signal.SIGINT)
        self.server_proc.communicate()
        self.assertEqual(0, self.server_proc.returncode)

    @staticmethod
    def wait_for_connection_to_server():
        client_config: ClientConfig = client_config_desc.from_default_file()

        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            while True:
                result = sock.connect_ex((
                    client_config.connection_config.server_host_name,
                    client_config.connection_config.server_port_number,
                ))
                if result == 0:
                    print("connected to server")
                    return
                else:
                    print("waiting for connection to server")
                    time.sleep(1)
                    continue

    def test_DescribeLineArgs(self):
        """
        Invokes client via generated `@/bin/run_argrelay_client` sending `ServerAction.DescribeArgs`.
        """
        test_line = f"{os.environ.get(client_command_env_var_name_)} goto h|"
        (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

        env_vars = os.environ.copy()
        env_vars[COMP_LINE_env_var] = command_line
        env_vars[COMP_POINT_env_var] = str(cursor_cpos)
        env_vars[COMP_TYPE_env_var] = str(CompType.DescribeArgs.value)
        env_vars[COMP_KEY_env_var] = UNKNOWN_COMP_KEY

        with change_to_known_repo_path("."):
            client_proc = subprocess.run(
                args = [
                    os.environ.get(client_command_env_var_name_),
                ],
                env = env_vars,
                capture_output = True
            )
            ret_code = client_proc.returncode
            if ret_code != 0:
                raise RuntimeError
            described_args = client_proc.stderr.decode("utf-8")
            eprint(f"described_args: {described_args}")
            self.maxDiff = None
            self.assertEqual(
                f"""
{TermColor.consumed_token.value}{os.environ.get(client_command_env_var_name_)}{TermColor.reset_style.value} {TermColor.consumed_token.value}goto{TermColor.reset_style.value} {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}h{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}{TermColor.reset_style.value} 
{ReservedEnvelopeClass.ClassFunction.name}: 2
{" " * indent_size}{TermColor.other_assigned_arg_value.value}FunctionCategory: external [{ArgSource.InitValue.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.explicit_pos_arg_value.value}ActionType: goto [{ArgSource.ExplicitPosArg.name}]{TermColor.reset_style.value}
{" " * indent_size}{TermColor.remaining_value.value}*ObjectSelector: ?{TermColor.reset_style.value} {TermColor.prefix_highlight.value}{TermColor.tangent_token_l_part.value}h{TermColor.reset_style.value}{TermColor.tangent_token_r_part.value}ost{TermColor.reset_style.value} service 
""",
                described_args
            )

    def test_ProposeArgValues(self):
        """
        Invokes client via generated `@/bin/run_argrelay_client` sending `ServerAction.ProposeArgValues`.
        """
        test_line = f"{os.environ.get(client_command_env_var_name_)} desc host dev upstream a|"
        (command_line, cursor_cpos) = parse_line_and_cpos(test_line)

        env_vars = os.environ.copy()
        env_vars[COMP_LINE_env_var] = command_line
        env_vars[COMP_POINT_env_var] = str(cursor_cpos)
        env_vars[COMP_TYPE_env_var] = str(CompType.PrefixShown.value)
        env_vars[COMP_KEY_env_var] = UNKNOWN_COMP_KEY

        with change_to_known_repo_path("."):
            client_proc = subprocess.run(
                args = [
                    os.environ.get(client_command_env_var_name_),
                ],
                env = env_vars,
                capture_output = True
            )
            ret_code = client_proc.returncode
            if ret_code != 0:
                raise RuntimeError
            proposed_args = client_proc.stdout.decode("utf-8").strip().splitlines()
            self.maxDiff = None
            self.assertEqual(
                [
                    "apac",
                    "amer",
                ],
                proposed_args
            )

    def test_RelayLineArgs(self):
        """
        Invokes client via generated `@/bin/run_argrelay_client` sending `ServerAction.RelayLineArgs`.
        """

        with change_to_known_repo_path("."):
            # Function "desc_host" ("desc host") uses `NoopDelegator`, so the test should always pass:
            client_proc = subprocess.run(
                args = f"{os.environ.get(client_command_env_var_name_)} desc host dev upstream amer".split(" "),
            )
            ret_code = client_proc.returncode
            if ret_code != 0:
                raise RuntimeError
