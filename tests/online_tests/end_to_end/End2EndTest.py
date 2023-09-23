import os
import signal
import socket
import subprocess
import time
from contextlib import closing
from unittest import TestCase, skipIf

from argrelay.misc_helper import get_argrelay_dir
from argrelay.runtime_data.ClientConfig import ClientConfig
from argrelay.schema_config_core_client.ClientConfigSchema import client_config_desc

client_command_env_var_name_ = "ARGRELAY_CLIENT_COMMAND"


def run_client_with_env_vars(
    env_vars,
):
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
    return client_proc


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
class End2EndTest(TestCase):
    """
    It tests both client and server started via their generated files in `@/bin/` dir.

    The test starts background server process to execute the client.

    It is probably "the fattest" test possible with end-to-end coverage while still using Python.
    The test controls startup of the server, unlike these tests (which rely on the server to be started manually):
    `test_relay_client_describe_line_args.py`
    `test_relay_client_propose_arg_values.py`
    `test_relay_client_relay_line_args.py`
    """

    server_proc = None

    def setUp(self):
        # Function "desc_host" ("desc host") uses `NoopDelegator`, so the test should always pass:
        self.server_proc = subprocess.Popen([
            f"{get_argrelay_dir()}/bin/run_argrelay_server",
        ])
        self.wait_for_connection_to_server()
        self.maxDiff = None

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


